"""
F-13 근태 관리 — 통합 테스트
"""

import pytest
from fastapi import status
from datetime import date, time, timedelta
import uuid
import random


def generate_email():
    """고유한 이메일 생성"""
    return f"test_{random.randint(10000, 99999)}@example.com"


def generate_business_number():
    """고유한 사업자등록번호 생성"""
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}"


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


async def create_company_and_select(client, token):
    """사업장 생성 후 선택하여 company_id 포함 토큰 반환"""
    # 사업장 생성
    company_response = await client.post(
        "/api/v1/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "테스트회사",
            "business_number": generate_business_number(),
            "representative_name": "홍길동",
            "industry_type": "it",
            "employee_count": 5
        }
    )

    if company_response.status_code != 201:
        return None, None

    company_data = company_response.json()
    company_id = company_data["data"]["id"]

    # 사업장 선택
    select_response = await client.post(
        f"/api/v1/companies/{company_id}/select",
        headers={"Authorization": f"Bearer {token}"}
    )

    if select_response.status_code == 200:
        select_data = select_response.json()
        company_token = select_data["data"]["access_token"]
        return company_id, company_token

    return None, None


async def create_employee(client, company_id, token, name="테스트직원"):
    """직원 생성"""
    response = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "id_number": "123456789012",
            "nationality": "한국",
            "employment_type": "정규직",
            "hire_date": "2020-01-01"
        }
    )

    if response.status_code == 201:
        return response.json()["data"]["id"]
    return None


class TestWorkRecordAPI:
    """근무 기록 API 테스트"""

    async def test_근무기록_생성_성공(self, client):
        """근무 기록을 정상적으로 생성할 수 있어야 함"""
        # 사용자 등록 및 로그인
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_id, company_token = await create_company_and_select(client, token)
        assert company_id is not None
        assert company_token is not None

        # 직원 생성
        employee_id = await create_employee(client, company_id, company_token)
        assert employee_id is not None

        # 근무 기록 생성
        today = date.today()
        response = await client.post(
            "/api/v1/attendance/records",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": employee_id,
                "work_date": today.isoformat(),
                "scheduled_start": "09:00",
                "scheduled_end": "18:00",
                "actual_start": "08:55",
                "actual_end": "18:30",
                "break_minutes": 60,
                "is_holiday": False,
                "memo": "정상 근무"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["employee_name"] == "테스트직원"
        assert data["data"]["overtime_minutes"] > 0

    async def test_근무기록_조회_성공(self, client):
        """근무 기록을 조회할 수 있어야 함"""
        # 사용자 등록 및 로그인
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_id, company_token = await create_company_and_select(client, token)
        assert company_id is not None

        # 직원 생성
        employee_id = await create_employee(client, company_id, company_token)
        assert employee_id is not None

        # 근무 기록 생성
        today = date.today()
        create_response = await client.post(
            "/api/v1/attendance/records",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": employee_id,
                "work_date": today.isoformat(),
                "scheduled_start": "09:00",
                "scheduled_end": "18:00",
                "actual_start": "09:00",
                "actual_end": "18:00",
                "break_minutes": 60,
                "is_holiday": False
            }
        )

        assert create_response.status_code == 201
        record_id = create_response.json()["data"]["id"]

        # 근무 기록 조회
        get_response = await client.get(
            f"/api/v1/attendance/records/{record_id}",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["success"] is True
        assert data["data"]["id"] == record_id

    async def test_근무기록_삭제_성공(self, client):
        """근무 기록을 삭제할 수 있어야 함"""
        # 사용자 등록 및 로그인
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_id, company_token = await create_company_and_select(client, token)
        assert company_id is not None

        # 직원 생성
        employee_id = await create_employee(client, company_id, company_token)
        assert employee_id is not None

        # 근무 기록 생성
        today = date.today()
        create_response = await client.post(
            "/api/v1/attendance/records",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": employee_id,
                "work_date": today.isoformat(),
                "scheduled_start": "09:00",
                "scheduled_end": "18:00",
                "actual_start": "09:00",
                "actual_end": "18:00",
                "break_minutes": 60
            }
        )

        assert create_response.status_code == 201
        record_id = create_response.json()["data"]["id"]

        # 근무 기록 삭제
        delete_response = await client.delete(
            f"/api/v1/attendance/records/{record_id}",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert delete_response.status_code == 204

    async def test_중복된_날짜_근무기록_생성_실패(self, client):
        """같은 직원의 같은 날짜에 근무 기록을 중복 생성할 수 없어야 함"""
        # 사용자 등록 및 로그인
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_id, company_token = await create_company_and_select(client, token)
        assert company_id is not None

        # 직원 생성
        employee_id = await create_employee(client, company_id, company_token)
        assert employee_id is not None

        today = date.today()

        # 첫 번째 근무 기록 생성
        response1 = await client.post(
            "/api/v1/attendance/records",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": employee_id,
                "work_date": today.isoformat(),
                "scheduled_start": "09:00",
                "scheduled_end": "18:00",
                "actual_start": "09:00",
                "actual_end": "18:00",
                "break_minutes": 60
            }
        )

        assert response1.status_code == 201

        # 두 번째 근무 기록 생성 시도
        response2 = await client.post(
            "/api/v1/attendance/records",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": employee_id,
                "work_date": today.isoformat(),
                "scheduled_start": "09:00",
                "scheduled_end": "18:00",
                "actual_start": "09:00",
                "actual_end": "18:00",
                "break_minutes": 60
            }
        )

        assert response2.status_code == 409

    async def test_템플릿_다운로드(self, client):
        """엑셀 템플릿을 다운로드할 수 있어야 함"""
        # 사용자 등록 및 로그인
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_id, company_token = await create_company_and_select(client, token)
        assert company_id is not None

        # 템플릿 다운로드
        response = await client.get(
            "/api/v1/attendance/import/template",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    async def test_월별_요약_조회(self, client):
        """월별 근무 기록 요약을 조회할 수 있어야 함"""
        # 사용자 등록 및 로그인
        token = await register_and_login(client)
        assert token is not None

        # 사업장 생성 및 선택
        company_id, company_token = await create_company_and_select(client, token)
        assert company_id is not None

        # 직원 생성
        employee_id = await create_employee(client, company_id, company_token)
        assert employee_id is not None

        # 근무 기록 생성
        today = date.today()
        response = await client.post(
            "/api/v1/attendance/records",
            headers={"Authorization": f"Bearer {company_token}"},
            json={
                "employee_id": employee_id,
                "work_date": today.isoformat(),
                "scheduled_start": "09:00",
                "scheduled_end": "18:00",
                "actual_start": "09:00",
                "actual_end": "18:00",
                "break_minutes": 60
            }
        )

        assert response.status_code == 201

        # 월별 요약 조회
        summary_response = await client.get(
            f"/api/v1/attendance/summary?year={today.year}&month={today.month}",
            headers={"Authorization": f"Bearer {company_token}"}
        )

        assert summary_response.status_code == 200
        data = summary_response.json()
        assert data["success"] is True
        assert "employees" in data["data"]
        assert "company_total" in data["data"]
