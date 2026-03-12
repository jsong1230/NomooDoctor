"""
F-10 컴플라이언스 대시보드 — 통합 테스트
"""

import pytest
from fastapi import status
import uuid
import random
from datetime import date, timedelta


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
            "name": name,
        }
    )

    # 로그인
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        }
    )

    if login_response.status_code == 200:
        data = login_response.json()
        return data.get("data", {}).get("access_token")
    return None


async def setup_company(client, token, employee_count=5):
    """사업장 생성 후 (company_id, company_token) 반환"""
    company_response = await client.post(
        "/api/v1/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "테스트사업장",
            "business_number": generate_business_number(),
            "representative_name": "홍길동",
            "industry_type": "it",
            "employee_count": employee_count,
        }
    )
    company_id = company_response.json()["data"]["id"]

    # 사업장 선택
    select_response = await client.post(
        f"/api/v1/companies/{company_id}/select",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    company_token = select_response.json()["data"]["access_token"]

    return company_id, company_token


async def create_employee(client, company_token, name="김직원"):
    """직원 생성 후 employee_id 반환"""
    employee_response = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {company_token}"},
        json={
            "name": name,
            "id_number": f"900101-{random.randint(1000000, 9999999)}",
            "nationality": "korean",
            "employment_type": "regular",
            "department": "개발팀",
            "position": "사원",
            "hire_date": "2024-01-01",
            "email": generate_email(),
            "bank_name": "신한은행",
            "bank_account": "110-123-456789",
        }
    )
    return employee_response.json()["data"]["id"]


async def create_contract_for_employee(client, company_token, employee_id, end_date=None):
    """직원에 대한 계약서 생성"""
    contract_data = {
        "employee_id": str(employee_id),
        "contract_type": "regular",
        "start_date": "2024-01-01",
        "work_location": "서울시 강남구",
        "work_hours_per_week": 40.0,
        "work_start_time": "09:00",
        "work_end_time": "18:00",
        "break_minutes": 60,
        "work_days": "mon,tue,wed,thu,fri",
        "wage_type": "monthly",
        "base_wage": 3000000,
    }
    if end_date:
        contract_data["end_date"] = end_date

    response = await client.post(
        "/api/v1/contracts/",
        headers={"Authorization": f"Bearer {company_token}"},
        json=contract_data,
    )
    return response.json().get("data", {}).get("id")


class TestComplianceScoreAPI:
    """리스크 스코어 API 테스트"""

    async def test_인증_없이_조회_실패(self, client):
        """인증 없이 리스크 스코어 조회 시 401 반환"""
        response = await client.get("/api/v1/compliance/score")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_사업장_미선택_시_403(self, client):
        """사업장 선택 없이 조회 시 403 반환"""
        token = await register_and_login(client)
        assert token is not None

        response = await client.get(
            "/api/v1/compliance/score",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_직원_없는_사업장_만점(self, client):
        """직원이 없는 사업장은 100점이어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/score",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["score"] == 100
        assert data["data"]["level"] == "green"
        assert data["data"]["total_employees"] == 0

    async def test_계약서_없는_직원_감점(self, client):
        """계약서 없는 직원이 있으면 감점되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        # 직원 1명 생성 (계약서 없이)
        await create_employee(client, company_token, "김직원")

        response = await client.get(
            "/api/v1/compliance/score",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # 근로계약서 미작성 -10점, 급여명세서 미발송 -5점 => 85점
        assert data["data"]["score"] <= 90
        assert data["data"]["employees_without_contract"] >= 1
        assert len(data["data"]["details"]) >= 1

    async def test_스코어_레벨_green(self, client):
        """80~100점이면 green"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/score",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        data = response.json()
        score = data["data"]["score"]
        level = data["data"]["level"]

        if score >= 80:
            assert level == "green"
        elif score >= 60:
            assert level == "yellow"
        else:
            assert level == "red"


class TestComplianceDetailsAPI:
    """리스크 상세 항목 API 테스트"""

    async def test_상세_항목_조회_성공(self, client):
        """리스크 상세 항목 조회 시 200과 함께 details가 반환되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/details",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "score" in data["data"]
        assert "level" in data["data"]
        assert "details" in data["data"]
        assert isinstance(data["data"]["details"], list)

    async def test_위반_항목에_해결_방법_포함(self, client):
        """위반 항목에 resolution 필드가 포함되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        # 직원 생성 (계약서 없이 -> 감점 항목 생성)
        await create_employee(client, company_token, "박직원")

        response = await client.get(
            "/api/v1/compliance/details",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        data = response.json()
        details = data["data"]["details"]
        assert len(details) >= 1

        for detail in details:
            assert "category" in detail
            assert "deduction" in detail
            assert "count" in detail
            assert "message" in detail
            assert "resolution" in detail
            assert detail["deduction"] < 0
            assert len(detail["resolution"]) > 0


class TestComplianceEventsAPI:
    """노무 이벤트 API 테스트"""

    async def test_이벤트_목록_조회_성공(self, client):
        """노무 이벤트 목록 조회 시 200 반환"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        today = date.today()
        response = await client.get(
            f"/api/v1/compliance/events?year={today.year}&month={today.month}",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "events" in data["data"]
        assert data["data"]["year"] == today.year
        assert data["data"]["month"] == today.month

    async def test_기본값으로_현재_연월_사용(self, client):
        """year, month 미지정 시 현재 연월을 사용해야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/events",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        today = date.today()
        assert data["data"]["year"] == today.year
        assert data["data"]["month"] == today.month

    async def test_급여_지급일_이벤트_포함(self, client):
        """이벤트 목록에 급여 지급일이 포함되어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        today = date.today()
        response = await client.get(
            f"/api/v1/compliance/events?year={today.year}&month={today.month}",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        data = response.json()
        events = data["data"]["events"]
        payroll_events = [e for e in events if e["event_type"] == "payroll_date"]
        assert len(payroll_events) >= 1


class TestUpcomingEventsAPI:
    """향후 이벤트 API 테스트"""

    async def test_향후_이벤트_조회_성공(self, client):
        """향후 이벤트 조회 시 200 반환"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/events/upcoming?days=30",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "events" in data["data"]
        assert data["data"]["period_days"] == 30

    async def test_조회_기간_파라미터(self, client):
        """days 파라미터로 조회 기간을 변경할 수 있어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/events/upcoming?days=7",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["period_days"] == 7


class TestRiskScoreHistoryAPI:
    """월별 리스크 스코어 변화 API 테스트"""

    async def test_히스토리_조회_성공(self, client):
        """월별 리스크 스코어 히스토리 조회 시 200 반환"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/score/history?months=6",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "history" in data["data"]
        assert len(data["data"]["history"]) == 6

    async def test_히스토리_항목_구조(self, client):
        """히스토리 각 항목에 year, month, score, level이 있어야 함"""
        token = await register_and_login(client)
        assert token is not None

        company_id, company_token = await setup_company(client, token)

        response = await client.get(
            "/api/v1/compliance/score/history?months=3",
            headers={"Authorization": f"Bearer {company_token}"},
        )

        data = response.json()
        history = data["data"]["history"]
        assert len(history) == 3

        for item in history:
            assert "year" in item
            assert "month" in item
            assert "score" in item
            assert "level" in item
            assert 0 <= item["score"] <= 100
            assert item["level"] in ["green", "yellow", "red"]
