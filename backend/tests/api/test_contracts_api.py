"""
F-04 근로계약서 자동 생성 — 통합 테스트
"""

import pytest
from fastapi import status
import uuid
import random
from datetime import date


def generate_business_number():
    """고유한 사업자등록번호 생성"""
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}"


def generate_email():
    """고유한 이메일 생성"""
    return f"test_{random.randint(10000, 99999)}@example.com"


async def register_and_login(client, email: str = None, password: str = "TestP@ss123", name: str = "테스트사용자"):
    """사용자 등록 후 로그인하여 토큰 반환"""
    if email is None:
        email = generate_email()

    # 회원가입
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name
        }
    )

    # 로그인
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    if login_response.status_code == 200:
        data = login_response.json()
        return data.get("data", {}).get("access_token")
    return None


async def create_test_company(client, token: str):
    """테스트용 사업장 생성"""
    response = await client.post(
        "/api/v1/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "테스트사업장",
            "business_number": generate_business_number(),
            "representative_name": "홍길동",
            "industry_type": "it",
            "employee_count": 5
        }
    )
    return response


async def select_company(client, token: str, company_id: str):
    """사업장 선택"""
    response = await client.post(
        f"/api/v1/companies/{company_id}/select",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    return response


async def create_test_employee(client, token: str):
    """테스트용 직원 생성"""
    response = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "홍길동",
            "id_number": "900101-1234567",
            "nationality": "korean",
            "employment_type": "regular",
            "department": "영업팀",
            "position": "사원",
            "hire_date": "2024-01-15"
        }
    )
    return response


class TestCreateContractAPI:
    """계약서 생성 API 테스트"""

    async def test_정상_계약서_초안_생성_성공(self, client):
        """정상적인 계약서 생성 요청 시 201과 함께 contract가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None, "로그인 실패"

        # 사업장 생성
        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        # 사업장 선택
        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        # 직원 등록
        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        # 계약서 생성
        response = await client.post(
            "/api/v1/contracts/",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": str(employee_id),
                "contract_type": "regular",
                "start_date": "2024-01-15",
                "work_location": "서울시 강남구",
                "work_hours_per_week": 40,
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "break_minutes": 60,
                "work_days": "월화수목금",
                "wage_type": "monthly",
                "base_wage": 2500000
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["employee_id"] == str(employee_id)
        assert data["data"]["contract_type"] == "regular"
        assert data["data"]["status"] == "draft"
        assert data["data"]["work_hours_per_week"] == 40
        assert data["data"]["base_wage"] == 2500000

    async def test_인증_없이_생성_실패(self, client):
        """인증 없이 계약서 생성 요청 시 401과 E-2001 에러가 반환되어야 함"""
        response = await client.post(
            "/api/v1/contracts/",
            json={
                "employee_id": str(uuid.uuid4()),
                "contract_type": "regular",
                "start_date": "2024-01-15",
                "work_location": "서울시 강남구",
                "work_hours_per_week": 40,
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "break_minutes": 60,
                "work_days": "월화수목금",
                "wage_type": "monthly",
                "base_wage": 2500000
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_최저임금_미달_경고(self, client):
        """최저임금 미달 시 422와 E-5001 에러가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성
        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        # 사업장 선택
        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        # 직원 등록
        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        # 최저임금 미달 계약서 생성 시도 (월 1,500,000원, 주 40시간)
        # 2026년 최저임금 기준: 시급 10,030원
        # 월 1,500,000원 / 209시간(월 근무시간) = 시급 약 7,177원 (미달)
        response = await client.post(
            "/api/v1/contracts/",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": str(employee_id),
                "contract_type": "regular",
                "start_date": "2024-01-15",
                "work_location": "서울시 강남구",
                "work_hours_per_week": 40,
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "break_minutes": 60,
                "work_days": "월화수목금",
                "wage_type": "monthly",
                "base_wage": 1500000
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False
        assert "error" in data


class TestListContractsAPI:
    """계약서 목록 조회 API 테스트"""

    async def test_정상_목록_조회_성공(self, client):
        """정상적인 목록 조회 요청 시 200과 함께 계약서 목록이 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성
        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        # 사업장 선택
        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        # 직원 등록
        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        # 계약서 등록 (2건)
        for i in range(2):
            await client.post(
                "/api/v1/contracts/",
                headers={"Authorization": f"Bearer {new_token}"},
                json={
                    "employee_id": str(employee_id),
                    "contract_type": "regular",
                    "start_date": "2024-01-15",
                    "work_location": "서울시 강남구",
                    "work_hours_per_week": 40,
                    "work_start_time": "09:00",
                    "work_end_time": "18:00",
                    "break_minutes": 60,
                    "work_days": "월화수목금",
                    "wage_type": "monthly",
                    "base_wage": 2500000
                }
            )

        # 목록 조회
        response = await client.get(
            "/api/v1/contracts/",
            headers={"Authorization": f"Bearer {new_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)


class TestGetContractAPI:
    """계약서 상세 조회 API 테스트"""

    async def test_정상_상세_조회_성공(self, client):
        """정상적인 상세 조회 요청 시 200과 함께 계약서 상세 정보가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성
        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        # 사업장 선택
        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        # 직원 등록
        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        # 계약서 등록
        contract_response = await client.post(
            "/api/v1/contracts/",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": str(employee_id),
                "contract_type": "regular",
                "start_date": "2024-01-15",
                "work_location": "서울시 강남구",
                "work_hours_per_week": 40,
                "work_start_time": "09:00",
                "work_end_time": "18:00",
                "break_minutes": 60,
                "work_days": "월화수목금",
                "wage_type": "monthly",
                "base_wage": 2500000
            }
        )
        contract_id = contract_response.json()["data"]["id"]

        # 상세 조회
        response = await client.get(
            f"/api/v1/contracts/{contract_id}",
            headers={"Authorization": f"Bearer {new_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(contract_id)
        assert data["data"]["employee_id"] == str(employee_id)
        assert data["data"]["contract_type"] == "regular"
        assert data["data"]["status"] == "draft"

    async def test_존재하지_않는_ID_조회_실패(self, client):
        """존재하지 않는 ID로 조회 시 404와 에러가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_response = await create_test_company(client, token)
        company_id = company_response.json()["data"]["id"]
        select_response = await select_company(client, token, company_id)
        new_token = select_response.json()["data"]["access_token"]

        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/contracts/{fake_id}",
            headers={"Authorization": f"Bearer {new_token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
