"""
F-14 전자서명 연동 — 통합 테스트
"""

import pytest
import random
import uuid
from fastapi import status


def generate_business_number():
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}"


def generate_email():
    return f"test_esign_{random.randint(10000, 99999)}@example.com"


async def register_and_login(client, email=None, password="TestP@ss123", name="테스트사용자"):
    if email is None:
        email = generate_email()
    await client.post("/api/v1/auth/register", json={"email": email, "password": password, "name": name})
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if login_resp.status_code == 200:
        return login_resp.json().get("data", {}).get("access_token")
    return None


async def setup_company_and_contract(client):
    """사업장 + 직원 + 계약서(draft) 생성 후 (token, contract_id) 반환"""
    token = await register_and_login(client)
    assert token is not None

    # 사업장 생성
    company_resp = await client.post(
        "/api/v1/companies/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "전자서명테스트사업장",
            "business_number": generate_business_number(),
            "representative_name": "홍길동",
            "industry_type": "it",
            "employee_count": 5,
        },
    )
    assert company_resp.status_code == status.HTTP_201_CREATED
    company_id = company_resp.json()["data"]["id"]

    # 사업장 선택
    select_resp = await client.post(
        f"/api/v1/companies/{company_id}/select",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert select_resp.status_code == status.HTTP_200_OK
    new_token = select_resp.json()["data"]["access_token"]

    # 직원 등록
    emp_resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {new_token}"},
        json={
            "name": "김서명",
            "id_number": "900101-1234567",
            "nationality": "korean",
            "employment_type": "regular",
            "department": "개발팀",
            "position": "사원",
            "hire_date": "2024-01-15",
        },
    )
    assert emp_resp.status_code == status.HTTP_201_CREATED
    employee_id = emp_resp.json()["data"]["id"]

    # 계약서 생성 (draft)
    contract_resp = await client.post(
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
            "base_wage": 2500000,
        },
    )
    assert contract_resp.status_code == status.HTTP_201_CREATED
    contract_id = contract_resp.json()["data"]["id"]

    return new_token, contract_id


class TestSignRequestAPI:

    async def test_전자서명_요청_성공(self, client):
        token, contract_id = await setup_company_and_contract(client)

        response = await client.post(
            f"/api/v1/contracts/{contract_id}/sign-request",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "signer_name": "김서명",
                "signer_email": "signer@example.com",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "sent"
        assert "signing_url" in data["data"]
        assert "sign_service_ref" in data["data"]

    async def test_전자서명_요청_미인증_실패(self, client):
        response = await client.post(
            f"/api/v1/contracts/{uuid.uuid4()}/sign-request",
            json={"signer_name": "김서명", "signer_email": "signer@example.com"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_전자서명_중복_요청_실패(self, client):
        token, contract_id = await setup_company_and_contract(client)

        # 첫 번째 요청 → 성공 (status: draft → sent)
        resp1 = await client.post(
            f"/api/v1/contracts/{contract_id}/sign-request",
            headers={"Authorization": f"Bearer {token}"},
            json={"signer_name": "김서명", "signer_email": "signer@example.com"},
        )
        assert resp1.status_code == status.HTTP_201_CREATED

        # 두 번째 요청 → 실패 (이미 sent 상태)
        resp2 = await client.post(
            f"/api/v1/contracts/{contract_id}/sign-request",
            headers={"Authorization": f"Bearer {token}"},
            json={"signer_name": "김서명", "signer_email": "signer@example.com"},
        )
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST
        assert resp2.json()["error"]["code"] == "E-9002"


class TestSignStatusAPI:

    async def test_서명_상태_조회_성공(self, client):
        token, contract_id = await setup_company_and_contract(client)

        # 서명 요청 발송
        await client.post(
            f"/api/v1/contracts/{contract_id}/sign-request",
            headers={"Authorization": f"Bearer {token}"},
            json={"signer_name": "김서명", "signer_email": "signer@example.com"},
        )

        # 상태 조회 (Mock 모드에서는 completed 반환)
        response = await client.get(
            f"/api/v1/contracts/{contract_id}/sign-status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] in ("sent", "signed")
        assert data["data"]["sign_service_ref"] is not None

    async def test_서명_미요청_상태_조회(self, client):
        token, contract_id = await setup_company_and_contract(client)

        response = await client.get(
            f"/api/v1/contracts/{contract_id}/sign-status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == "draft"
        assert data["data"]["sign_service_ref"] is None


class TestSignedPdfAPI:

    async def test_서명완료_PDF_다운로드_성공(self, client):
        token, contract_id = await setup_company_and_contract(client)

        # 서명 요청 → 상태 조회 (Mock: 자동 서명 완료)
        await client.post(
            f"/api/v1/contracts/{contract_id}/sign-request",
            headers={"Authorization": f"Bearer {token}"},
            json={"signer_name": "김서명", "signer_email": "signer@example.com"},
        )
        # Mock 모드: 상태 조회하면 자동으로 signed 처리됨
        await client.get(
            f"/api/v1/contracts/{contract_id}/sign-status",
            headers={"Authorization": f"Bearer {token}"},
        )

        # PDF 다운로드
        response = await client.get(
            f"/api/v1/contracts/{contract_id}/signed-pdf",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "pdf" in response.headers.get("content-type", "").lower()

    async def test_서명_전_PDF_다운로드_실패(self, client):
        token, contract_id = await setup_company_and_contract(client)

        response = await client.get(
            f"/api/v1/contracts/{contract_id}/signed-pdf",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestModusignWebhookAPI:

    async def test_웹훅_서명완료_처리(self, client):
        token, contract_id = await setup_company_and_contract(client)

        # 서명 요청 → sign_service_ref 획득
        sign_resp = await client.post(
            f"/api/v1/contracts/{contract_id}/sign-request",
            headers={"Authorization": f"Bearer {token}"},
            json={"signer_name": "김서명", "signer_email": "signer@example.com"},
        )
        sign_ref = sign_resp.json()["data"]["sign_service_ref"]

        # 웹훅 수신
        response = await client.post(
            "/api/v1/webhooks/modusign",
            json={
                "event": "document.completed",
                "document_id": sign_ref,
                "completed_at": "2026-03-12T12:00:00+00:00",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"

        # 상태 확인
        status_resp = await client.get(
            f"/api/v1/contracts/{contract_id}/sign-status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert status_resp.json()["data"]["status"] == "signed"

    async def test_웹훅_존재하지_않는_문서(self, client):
        response = await client.post(
            "/api/v1/webhooks/modusign",
            json={
                "event": "document.completed",
                "document_id": "nonexistent_doc_id",
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
