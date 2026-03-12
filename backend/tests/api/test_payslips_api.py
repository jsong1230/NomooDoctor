"""
F-07 급여명세서 생성 및 발송 — 통합 테스트
"""

import pytest
from fastapi import status
import uuid
import random
from decimal import Decimal
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


async def setup_company_and_employee(client, token):
    """사업장과 직원 생성 후 (company_id, employee_id, company_token) 반환

    company_token: company_id가 포함된 JWT — payslip 등 회사 컨텍스트가 필요한 API에 사용
    """
    # 사업장 생성
    company_response = await client.post(
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
    company_id = company_response.json()["data"]["id"]

    # 사업장 선택 — company_id 포함된 새 토큰 발급
    select_response = await client.post(
        f"/api/v1/companies/{company_id}/select",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    company_token = select_response.json()["data"]["access_token"]

    # 직원 생성 (사업장이 포함된 새 토큰 사용, 이메일 포함)
    employee_response = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {company_token}"},
        json={
            "name": "김직원",
            "id_number": f"900101-{random.randint(1000000, 9999999)}",
            "nationality": "korean",
            "employment_type": "regular",
            "department": "개발팀",
            "position": "사원",
            "hire_date": "2024-01-01",
            "email": generate_email(),
            "bank_name": "신한은행",
            "bank_account": "110-123-456789"
        }
    )
    employee_id = employee_response.json()["data"]["id"]

    return company_id, employee_id, company_token


class TestCreatePayslipAPI:
    """급여명세서 생성 API 테스트"""

    async def test_정상_급여명세서_생성_성공(self, client):
        """정상적인 급여명세서 생성 시 201과 함께 payslip이 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000,
                "weekly_allowance": 0,
                "overtime_pay": 150000,
                "night_pay": 0,
                "holiday_pay": 0,
                "meal_allowance": 100000,
                "transport_allowance": 50000,
                "national_pension": 112500,
                "health_insurance": 88625,
                "long_term_care": 11487,
                "employment_insurance": 22500,
                "income_tax": 13210,
                "local_income_tax": 1321
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["employee_id"] == str(employee_id)
        assert data["data"]["year"] == 2024
        assert data["data"]["month"] == 12
        assert data["data"]["send_status"] == "pending"

    async def test_인증_없이_생성_실패(self, client):
        """인증 없이 급여명세서 생성 시 401 반환"""
        response = await client.post(
            "/api/v1/payslips/",
            json={
                "employee_id": str(uuid.uuid4()),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_존재하지_않는_직원_생성_실패(self, client):
        """존재하지 않는 직원 ID로 생성 시 404 반환"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 선택 없이 바로 생성 시 403(회사 미선택) 또는 사업장 선택 후 가짜 직원으로 404 기대
        company_response = await client.post(
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
        company_id = company_response.json()["data"]["id"]

        select_response = await client.post(
            f"/api/v1/companies/{company_id}/select",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )
        company_token = select_response.json()["data"]["access_token"]

        fake_employee_id = uuid.uuid4()
        response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(fake_employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_실수령액_자동_계산(self, client):
        """지급총액 - 공제총액 = 실수령액이 자동 계산되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2000000,
                "weekly_allowance": 0,
                "overtime_pay": 0,
                "night_pay": 0,
                "holiday_pay": 0,
                "meal_allowance": 0,
                "transport_allowance": 0,
                "national_pension": 90000,
                "health_insurance": 70000,
                "long_term_care": 9000,
                "employment_insurance": 18000,
                "income_tax": 10000,
                "local_income_tax": 1000
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # 지급총액: 2000000, 공제총액: 90000+70000+9000+18000+10000+1000 = 198000
        # 실수령액: 2000000 - 198000 = 1802000
        assert data["data"]["total_payment"] == 2000000
        assert data["data"]["total_deduction"] == 198000
        assert data["data"]["net_salary"] == 1802000


class TestListPayslipsAPI:
    """급여명세서 목록 조회 API 테스트"""

    async def test_정상_목록_조회_성공(self, client):
        """정상적인 목록 조회 시 200과 함께 payslip 목록이 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 급여명세서 생성
        await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000
            }
        )

        response = await client.get(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    async def test_연월_필터링(self, client):
        """year, month로 필터링 가능해야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 여러 월의 급여명세서 생성
        for month in [10, 11, 12]:
            await client.post(
                "/api/v1/payslips/",
                headers={"Authorization": f"Bearer {company_token}"},
                json={
                    "employee_id": str(employee_id),
                    "year": 2024,
                    "month": month,
                    "payment_date": f"2024-{month:02d}-25",
                    "base_salary": 2500000
                }
            )

        response = await client.get(
            "/api/v1/payslips/?year=2024&month=11",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(p["year"] == 2024 and p["month"] == 11 for p in data["data"])


class TestGetPayslipAPI:
    """급여명세서 상세 조회 API 테스트"""

    async def test_정상_상세_조회_성공(self, client):
        """정상적인 상세 조회 시 200과 함께 payslip 상세 정보가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 급여명세서 생성
        create_response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000
            }
        )
        payslip_id = create_response.json()["data"]["id"]

        # 상세 조회
        response = await client.get(
            f"/api/v1/payslips/{payslip_id}",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(payslip_id)
        assert "employee_name" in data["data"]
        assert "company_name" in data["data"]

    async def test_존재하지_않는_ID_조회_실패(self, client):
        """존재하지 않는 ID로 조회 시 404 반환"""
        token = await register_and_login(client)
        assert token is not None

        # 사업장 선택 후 토큰 발급
        company_response = await client.post(
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
        company_id = company_response.json()["data"]["id"]
        select_response = await client.post(
            f"/api/v1/companies/{company_id}/select",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )
        company_token = select_response.json()["data"]["access_token"]

        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/payslips/{fake_id}",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPayslipPDFAPI:
    """급여명세서 PDF 다운로드 API 테스트"""

    async def test_PDF_다운로드_성공(self, client):
        """PDF 다운로드 요청 시 PDF 파일이 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 급여명세서 생성
        create_response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000
            }
        )
        payslip_id = create_response.json()["data"]["id"]

        # PDF 다운로드
        response = await client.get(
            f"/api/v1/payslips/{payslip_id}/pdf",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0


class TestSendPayslipAPI:
    """급여명세서 발송 API 테스트"""

    async def test_이메일_발송_요청_성공(self, client):
        """이메일 발송 요청 시 200과 함께 발송 상태가 업데이트되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 급여명세서 생성
        create_response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000
            }
        )
        payslip_id = create_response.json()["data"]["id"]

        # 이메일 발송
        response = await client.post(
            f"/api/v1/payslips/{payslip_id}/send",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "method": "email"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["send_status"] in ["sent", "pending"]  # 비동기 발송일 수 있음

    async def test_발송_상태_추적(self, client):
        """발송 후 상태가 추적되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 급여명세서 생성
        create_response = await client.post(
            "/api/v1/payslips/",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": str(employee_id),
                "year": 2024,
                "month": 12,
                "payment_date": "2024-12-25",
                "base_salary": 2500000
            }
        )
        payslip_id = create_response.json()["data"]["id"]

        # 발송 전 상태 확인
        detail_response = await client.get(
            f"/api/v1/payslips/{payslip_id}",
            headers={"Authorization": f"Bearer {company_token}"}
        )
        assert detail_response.json()["data"]["send_status"] == "pending"

        # 발송
        await client.post(
            f"/api/v1/payslips/{payslip_id}/send",
            headers={"Authorization": f"Bearer {company_token}"},
            json={"method": "email"}
        )

        # 발송 후 상태 확인
        after_response = await client.get(
            f"/api/v1/payslips/{payslip_id}",
            headers={"Authorization": f"Bearer {company_token}"}
        )
        assert after_response.json()["data"]["send_status"] in ["sent", "pending"]


class TestEmployeePayslipHistoryAPI:
    """직원별 급여 히스토리 API 테스트"""

    async def test_직원별_급여_히스토리_조회(self, client):
        """특정 직원의 급여 히스토리를 조회할 수 있어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, employee_id, company_token = await setup_company_and_employee(client, token)

        # 여러 월의 급여명세서 생성
        for month in [10, 11, 12]:
            await client.post(
                "/api/v1/payslips/",
                headers={"Authorization": f"Bearer {company_token}"},
                json={
                    "employee_id": str(employee_id),
                    "year": 2024,
                    "month": month,
                    "payment_date": f"2024-{month:02d}-25",
                    "base_salary": 2500000 + (month * 10000)  # 매월 인상
                }
            )

        # 직원별 히스토리 조회
        response = await client.get(
            f"/api/v1/employees/{employee_id}/payslips",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

    async def test_다른_회사_직원_히스토리_접근_불가(self, client):
        """다른 회사 직원의 히스토리는 조회할 수 없어야 함"""
        # 첫 번째 사용자와 회사
        token1 = await register_and_login(client)
        company_id1, employee_id1, company_token1 = await setup_company_and_employee(client, token1)

        # 두 번째 사용자와 회사
        token2 = await register_and_login(client)
        company_id2, employee_id2, company_token2 = await setup_company_and_employee(client, token2)

        # 첫 번째 사용자가 두 번째 사용자의 직원 히스토리 조회 시도
        response = await client.get(
            f"/api/v1/employees/{employee_id2}/payslips",
            headers={"Authorization": f"Bearer {company_token1}"}
        )

        # 403 또는 404 반환
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
