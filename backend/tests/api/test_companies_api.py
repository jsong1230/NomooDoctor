"""
F-02 사업장 관리 — 통합 테스트
"""

import pytest
from fastapi import status
import uuid
import random


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


class TestCreateCompanyAPI:
    """사업장 등록 API 테스트"""

    async def test_정상_사업장_등록_성공(self, client):
        """정상적인 정보로 사업장 등록 요청 시 201과 함께 company가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None, "로그인 실패"

        response = await client.post(
            "/api/v1/companies/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "business_name": "노무닥터 주식회사",
                "business_number": generate_business_number(),
                "representative_name": "홍길동",
                "industry_type": "it",
                "employee_count": 5,
                "address": "서울특별시 강남구 테헤란로 123",
                "postal_code": "06123",
                "phone": "02-1234-5678"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["business_name"] == "노무닥터 주식회사"
        assert data["data"]["employee_count"] == 5
        assert data["data"]["work_rule_required"] is False

    async def test_인증_없이_등록_실패(self, client):
        """인증 없이 사업장 등록 요청 시 401과 E-2001 에러가 반환되어야 함"""
        response = await client.post(
            "/api/v1/companies/",
            json={
                "business_name": "테스트사업장",
                "business_number": generate_business_number(),
                "representative_name": "홍길동",
                "industry_type": "it",
                "employee_count": 5
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_10인_이상_사업장_등록_work_rule_required_TRUE(self, client):
        """10인 이상 사업장 등록 시 work_rule_required가 TRUE여야 함"""
        token = await register_and_login(client)
        assert token is not None

        response = await client.post(
            "/api/v1/companies/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "business_name": "중견기업",
                "business_number": generate_business_number(),
                "representative_name": "김대표",
                "industry_type": "manufacturing",
                "employee_count": 50
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["data"]["work_rule_required"] is True


class TestListCompaniesAPI:
    """사업장 목록 조회 API 테스트"""

    async def test_정상_목록_조회_성공(self, client):
        """정상적인 목록 조회 요청 시 200과 함께 사용자 사업장 목록이 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        response = await client.get(
            "/api/v1/companies/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    async def test_인증_없이_목록_조회_실패(self, client):
        """인증 없이 목록 조회 요청 시 401과 E-2001 에러가 반환되어야 함"""
        response = await client.get("/api/v1/companies/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCompanyAPI:
    """사업장 상세 조회 API 테스트"""

    async def test_정상_상세_조회_성공(self, client):
        """정상적인 상세 조회 요청 시 200과 함께 company 상세 정보가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 먼저 사업장 등록
        create_response = await client.post(
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
        company_id = create_response.json()["data"]["id"]

        # 상세 조회
        response = await client.get(
            f"/api/v1/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(company_id)

    async def test_존재하지_않는_ID_조회_실패(self, client):
        """존재하지 않는 ID로 조회 시 404와 E-4001 에러가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/companies/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateCompanyAPI:
    """사업장 수정 API 테스트"""

    async def test_정상_수정_성공(self, client):
        """정상적인 수정 요청 시 200과 함께 수정된 company가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 등록
        create_response = await client.post(
            "/api/v1/companies/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "business_name": "원래이름",
                "business_number": generate_business_number(),
                "representative_name": "홍길동",
                "industry_type": "it",
                "employee_count": 5
            }
        )
        company_id = create_response.json()["data"]["id"]

        # 수정
        response = await client.put(
            f"/api/v1/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "business_name": "바뀐이름",
                "employee_count": 15,
                "address": "서울특별시 강남구 새로운 주소"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["business_name"] == "바뀐이름"
        assert data["data"]["employee_count"] == 15


class TestDeleteCompanyAPI:
    """사업장 삭제 API 테스트 (Soft Delete)"""

    async def test_정상_삭제_성공(self, client):
        """정상적인 삭제 요청 시 200과 함께 is_deleted가 TRUE로 설정되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 등록
        create_response = await client.post(
            "/api/v1/companies/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "business_name": "삭제될사업장",
                "business_number": generate_business_number(),
                "representative_name": "홍길동",
                "industry_type": "it",
                "employee_count": 5
            }
        )
        company_id = create_response.json()["data"]["id"]

        # 삭제
        response = await client.delete(
            f"/api/v1/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"confirmation": "삭제될사업장"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True


class TestSelectCompanyAPI:
    """사업장 선택 API 테스트"""

    async def test_정상_사업장_선택_성공(self, client):
        """정상적인 사업장 선택 시 200과 함께 새 tokens가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 등록
        create_response = await client.post(
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
        company_id = create_response.json()["data"]["id"]

        # 사업장 선택
        response = await client.post(
            f"/api/v1/companies/{company_id}/select",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
