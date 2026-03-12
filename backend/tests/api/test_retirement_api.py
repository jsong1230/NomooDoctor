"""
F-09 퇴직금/해고 계산기 — 통합 테스트
"""

import pytest
from fastapi import status
from datetime import date, timedelta
from decimal import Decimal
import random
import uuid


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


async def create_test_employee(client, token: str, hire_date: str = "2024-01-15"):
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
            "hire_date": hire_date
        }
    )
    return response


class TestSeveranceCalculateAPI:
    """퇴직금 계산 API 테스트"""

    async def test_정상_퇴직금_계산_수동입력(self, client):
        """월별 급여를 수동 입력하여 정상 계산"""
        # 사용자/회사/직원 준비
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        # 입사 2024-01-15, 퇴사 2026-03-31 (재직 807일)
        employee_response = await create_test_employee(client, new_token, "2024-01-15")
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        # 퇴직금 계산
        response = await client.post(
            "/api/v1/retirement/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "resign_date": "2026-03-31",
                "annual_bonus": 0,
                "unused_annual_leave_days": 0,
                "monthly_wages": [
                    {
                        "year": 2026,
                        "month": 1,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    },
                    {
                        "year": 2026,
                        "month": 2,
                        "total_wage": 3000000,
                        "days_in_month": 28
                    },
                    {
                        "year": 2026,
                        "month": 3,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    }
                ]
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["employee_id"] == employee_id
        assert data["employee_name"] == "홍길동"
        assert data["hire_date"] == "2024-01-15"
        assert data["resign_date"] == "2026-03-31"
        assert data["total_service_days"] > 0
        assert data["average_daily_wage"] > 0
        assert data["severance_pay"] > 0
        assert data["total_payment"] > 0
        assert data["eligible"] == True

    async def test_재직기간_1년미만_E5010(self, client):
        """재직기간 1년 미만 시 E-5010 에러"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        # 입사 2025-10-01, 퇴사 2026-03-31 (재직 182일)
        employee_response = await create_test_employee(client, new_token, "2025-10-01")
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/retirement/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "resign_date": "2026-03-31",
                "annual_bonus": 0,
                "unused_annual_leave_days": 0,
                "monthly_wages": [
                    {
                        "year": 2026,
                        "month": 1,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    },
                    {
                        "year": 2026,
                        "month": 2,
                        "total_wage": 3000000,
                        "days_in_month": 28
                    },
                    {
                        "year": 2026,
                        "month": 3,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    }
                ]
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error = response.json()["error"]
        assert error["code"] == "E-5010"

    async def test_퇴사일_입사일이전_E5011(self, client):
        """퇴사일이 입사일 이전 시 E-5011 에러"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token, "2024-01-15")
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/retirement/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "resign_date": "2024-01-01",  # 입사일보다 이전
                "annual_bonus": 0,
                "unused_annual_leave_days": 0,
                "monthly_wages": [
                    {
                        "year": 2026,
                        "month": 1,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    },
                    {
                        "year": 2026,
                        "month": 2,
                        "total_wage": 3000000,
                        "days_in_month": 28
                    },
                    {
                        "year": 2026,
                        "month": 3,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    }
                ]
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error = response.json()["error"]
        assert error["code"] == "E-5011"

    async def test_직원없음_E4004(self, client):
        """존재하지 않는 직원 ID로 요청 시 E-4004 에러"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        response = await client.post(
            "/api/v1/retirement/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": str(uuid.uuid4()),  # 존재하지 않는 ID
                "resign_date": "2026-03-31",
                "annual_bonus": 0,
                "unused_annual_leave_days": 0,
                "monthly_wages": [
                    {
                        "year": 2026,
                        "month": 1,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    },
                    {
                        "year": 2026,
                        "month": 2,
                        "total_wage": 3000000,
                        "days_in_month": 28
                    },
                    {
                        "year": 2026,
                        "month": 3,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    }
                ]
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()["error"]
        assert error["code"] == "E-4004"


class TestSeveranceSaveAPI:
    """퇴직금 저장 API 테스트"""

    async def test_정상_퇴직금_저장_201(self, client):
        """정상적인 퇴직금 저장 요청 시 201 상태코드 반환"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token, "2024-01-15")
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/retirement/severance",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "resign_date": "2026-03-31",
                "annual_bonus": 0,
                "unused_annual_leave_days": 0,
                "monthly_wages": [
                    {
                        "year": 2026,
                        "month": 1,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    },
                    {
                        "year": 2026,
                        "month": 2,
                        "total_wage": 3000000,
                        "days_in_month": 28
                    },
                    {
                        "year": 2026,
                        "month": 3,
                        "total_wage": 3000000,
                        "days_in_month": 31
                    }
                ]
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert "id" in data
        assert data["status"] == "calculated"
        assert data["severance_pay"] > 0


class TestTerminationGuideAPI:
    """해고 절차 가이드 API 테스트"""

    async def test_자발적퇴사_위험도LOW(self, client):
        """자발적 퇴사 시 위험도 LOW"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/retirement/termination-guide",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "termination_type": "resignation",
                "reason": "개인 사정",
                "risk_factors": {}
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["termination_type"] == "resignation"
        assert data["risk_level"] == "LOW"
        assert len(data["checklist"]) > 0
        assert "disclaimer" in data

    async def test_해고_위험도MEDIUM(self, client):
        """해고(위험 요소 없음) 시 위험도 MEDIUM"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/retirement/termination-guide",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "termination_type": "dismissal",
                "reason": "경영상 사유",
                "risk_factors": {}
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["termination_type"] == "dismissal"
        assert data["risk_level"] == "MEDIUM"
        assert data["advance_notice"]["required"] == True

    async def test_임신직원_해고_위험도EMERGENCY(self, client):
        """임신 중인 직원 해고 시 위험도 EMERGENCY"""
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        response = await client.post(
            "/api/v1/retirement/termination-guide",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "termination_type": "dismissal",
                "reason": "경영상 사유",
                "risk_factors": {
                    "is_pregnant": True
                }
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["risk_level"] == "EMERGENCY"
        assert len(data["risk_warnings"]) > 0
        assert data["risk_warnings"][0]["severity"] == "EMERGENCY"
