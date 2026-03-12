"""
F-05 급여 자동 계산기 — 통합 테스트
"""

import pytest
from fastapi import status
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


class TestCalculatePayrollAPI:
    """급여 계산 API 테스트"""

    async def test_정상_급여_계산_성공(self, client):
        """정상적인 급여 계산 요청 시 200과 함께 계산 결과가 반환되어야 함"""
        # Arrange: 인증 및 사업장/직원 생성
        token = await register_and_login(client)
        assert token is not None, "로그인 실패"

        company_response = await create_test_company(client, token)
        assert company_response.status_code == status.HTTP_201_CREATED
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        assert select_response.status_code == status.HTTP_200_OK
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        assert employee_response.status_code == status.HTTP_201_CREATED
        employee_id = employee_response.json()["data"]["id"]

        # Act: 급여 계산 요청
        response = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 600,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert: 계산 결과 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        payroll = data["data"]
        # 필수 필드 확인
        assert "total_gross" in payroll
        assert "total_deduction" in payroll
        assert "net_pay" in payroll

        # 지급 항목 확인
        assert payroll.get("base_wage") == 2500000
        assert payroll.get("meal_allowance") == 100000
        assert payroll.get("transport_allowance") == 50000

        # 공제 항목 확인
        assert "national_pension" in payroll
        assert "health_insurance" in payroll
        assert "long_term_care" in payroll
        assert "employment_insurance" in payroll
        assert "income_tax" in payroll
        assert "local_income_tax" in payroll

    async def test_인증_없이_계산_실패(self, client):
        """인증 없이 급여 계산 요청 시 401과 에러가 반환되어야 함"""
        # Arrange: 인증 없이 요청
        fake_employee_id = uuid.uuid4()

        # Act: 급여 계산 요청
        response = await client.post(
            "/api/v1/payroll/calculate",
            json={
                "employee_id": str(fake_employee_id),
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 600,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert: 401 응답 확인
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_연장수당_계산_포함(self, client):
        """연장수당이 포함된 급여 계산 시 정확히 계산되어야 함"""
        # Arrange: 인증 및 사업장/직원 생성
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

        # Act: 연장수당(600분 = 10시간) 포함 계산
        base_wage = 2500000
        overtime_minutes = 600  # 10시간

        response = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": base_wage,
                "overtime_minutes": overtime_minutes,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert: 연장수당 계산 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

        payroll = data["data"]
        assert "overtime_pay" in payroll
        assert payroll["overtime_pay"] > 0

    async def test_야간수당_계산_포함(self, client):
        """야간수당이 포함된 급여 계산 시 정확히 계산되어야 함"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        employee_id = employee_response.json()["data"]["id"]

        # Act: 야간수당(300분 = 5시간) 포함 계산
        response = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 0,
                "night_minutes": 300,  # 5시간
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        payroll = data["data"]
        assert "night_pay" in payroll
        assert payroll["night_pay"] > 0

    async def test_휴일수당_계산_포함(self, client):
        """휴일수당이 포함된 급여 계산 시 정확히 계산되어야 함"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        employee_id = employee_response.json()["data"]["id"]

        # Act: 휴일수당(480분 = 8시간) 포함 계산
        response = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 0,
                "night_minutes": 0,
                "holiday_minutes": 480,  # 8시간
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        payroll = data["data"]
        assert "holiday_pay" in payroll
        assert payroll["holiday_pay"] > 0

    async def test_가족수에_따른_소득세_계산(self, client):
        """가족 수에 따른 소득세 계산 확인"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        employee_id = employee_response.json()["data"]["id"]

        # Act 1: 가족 수 1인
        response1 = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 0,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Act 2: 가족 수 3인
        response2 = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 0,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 3
            }
        )

        # Assert: 가족 수가 많을수록 소득세가 낮아야 함
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

        tax1 = response1.json()["data"]["income_tax"]
        tax2 = response2.json()["data"]["income_tax"]

        # 가족 수가 많을수록 세금이 적어야 함
        assert tax1 >= tax2

    async def test_존재하지_않는_직원_계산_실패(self, client):
        """존재하지 않는 직원 ID로 급여 계산 시 실패해야 함"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        new_token = select_response.json()["data"]["access_token"]

        fake_employee_id = uuid.uuid4()

        # Act: 존재하지 않는 직원으로 계산
        response = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": str(fake_employee_id),
                "pay_year": 2024,
                "pay_month": 1,
                "base_wage": 2500000,
                "overtime_minutes": 0,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert: 404 응답
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_필수_필드_누락_계산_실패(self, client):
        """필수 필드 누락 시 급여 계산 실패해야 함"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        company_response = await create_test_company(client, token)
        company_id = company_response.json()["data"]["id"]

        select_response = await select_company(client, token, company_id)
        new_token = select_response.json()["data"]["access_token"]

        employee_response = await create_test_employee(client, new_token)
        employee_id = employee_response.json()["data"]["id"]

        # Act: 기본급 누락
        response = await client.post(
            "/api/v1/payroll/calculate",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "employee_id": employee_id,
                "pay_year": 2024,
                "pay_month": 1,
                # base_wage 누락
                "overtime_minutes": 0,
                "night_minutes": 0,
                "holiday_minutes": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "income_tax_family_count": 1
            }
        )

        # Assert: 422 Validation Error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetRatesAPI:
    """요율 조회 API 테스트"""

    async def test_정상_요율_조회_성공(self, client):
        """정상적인 요율 조회 요청 시 200과 함께 요율 정보가 반환되어야 함"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        # Act: 요율 조회
        response = await client.get(
            "/api/v1/payroll/rates",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: 요율 정보 확인
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        rates = data["data"]
        # 필수 요율 필드 확인
        assert "national_pension_rate" in rates
        assert "health_insurance_rate" in rates
        assert "long_term_care_rate" in rates
        assert "employment_insurance_rate" in rates
        assert "local_income_tax_rate" in rates
        assert "overtime_rate" in rates
        assert "night_rate" in rates
        assert "holiday_rate_normal" in rates
        assert "holiday_rate_over" in rates

    async def test_인증_없이_요율_조회_실패(self, client):
        """인증 없이 요율 조회 요청 시 401과 에러가 반환되어야 함"""
        # Act: 인증 없이 요율 조회
        response = await client.get("/api/v1/payroll/rates")

        # Assert: 401 응답
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_요율값_유효성_확인(self, client):
        """요율 값이 올바른 범위에 있는지 확인"""
        # Arrange
        token = await register_and_login(client)
        assert token is not None

        # Act
        response = await client.get(
            "/api/v1/payroll/rates",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        rates = response.json()["data"]

        # 국민연금: 4.5%
        assert rates["national_pension_rate"] == "0.045"
        # 건강보험: 3.545%
        assert rates["health_insurance_rate"] == "0.03545"
        # 장기요양: 12.95%
        assert rates["long_term_care_rate"] == "0.1295"
        # 고용보험: 0.9%
        assert rates["employment_insurance_rate"] == "0.009"
        # 지방소득세: 10%
        assert rates["local_income_tax_rate"] == "0.1"
        # 연장수당: 1.5배
        assert rates["overtime_rate"] == "1.5"
        # 야간수당: 0.5배 (추가분)
        assert rates["night_rate"] == "0.5"
        # 휴일수당 8시간 이내: 1.5배
        assert rates["holiday_rate_normal"] == "1.5"
        # 휴일수당 8시간 초과: 2.0배
        assert rates["holiday_rate_over"] == "2.0"
