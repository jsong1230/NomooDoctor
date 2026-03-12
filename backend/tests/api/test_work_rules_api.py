# WorkRule API 테스트
import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
async def test_get_templates(client: AsyncClient, auth_token: str, company_id: str):
    """템플릿 목록 조회 테스트"""
    response = await client.get(
        "/api/v1/work-rules/templates",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]) > 0


@pytest.mark.asyncio
async def test_create_work_rule(client: AsyncClient, auth_token: str, company_id: str):
    """취업규칙 생성 테스트"""
    response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "manufacturing",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "draft"
    assert data["data"]["industry_type"] == "manufacturing"
    assert data["data"]["version"] == 1
    assert len(data["data"]["content"]["sections"]) == 14


@pytest.mark.asyncio
async def test_list_work_rules(client: AsyncClient, auth_token: str, company_id: str):
    """취업규칙 목록 조회 테스트"""
    # 먼저 취업규칙 생성
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "service",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201

    # 목록 조회
    response = await client.get(
        "/api/v1/work-rules/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0


@pytest.mark.asyncio
async def test_get_work_rule(client: AsyncClient, auth_token: str, company_id: str):
    """취업규칙 상세 조회 테스트"""
    # 먼저 취업규칙 생성
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "food_service",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # 상세 조회
    response = await client.get(
        f"/api/v1/work-rules/{work_rule_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == work_rule_id


@pytest.mark.asyncio
async def test_update_work_rule(client: AsyncClient, auth_token: str, company_id: str):
    """취업규칙 수정 테스트"""
    # 먼저 취업규칙 생성
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "it",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # 수정
    response = await client.put(
        f"/api/v1/work-rules/{work_rule_id}",
        json={
            "status": "under_review",
            "effective_date": "2026-05-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "under_review"


@pytest.mark.asyncio
async def test_delete_work_rule(client: AsyncClient, auth_token: str, company_id: str):
    """취업규칙 삭제 테스트"""
    # 먼저 취업규칙 생성
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "manufacturing",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # 삭제
    response = await client.delete(
        f"/api/v1/work-rules/{work_rule_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_generate_ai_draft(client: AsyncClient, auth_token: str, company_id: str):
    """AI 초안 생성 테스트"""
    # 먼저 취업규칙 생성
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "manufacturing",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # AI 초안 생성
    response = await client.post(
        f"/api/v1/work-rules/{work_rule_id}/generate",
        json={
            "industry_type": "manufacturing",
            "additional_context": "직원 15명, 교대근무 운영"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["ai_generated"] is True


@pytest.mark.asyncio
async def test_revise_work_rule(client: AsyncClient, auth_token: str, company_id: str):
    """개정 테스트"""
    # 먼저 취업규칙 생성 및 활성화
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "manufacturing",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # 상태를 active로 변경
    update_response = await client.put(
        f"/api/v1/work-rules/{work_rule_id}",
        json={"status": "active"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert update_response.status_code == 200

    # 개정
    response = await client.post(
        f"/api/v1/work-rules/{work_rule_id}/revise",
        json={
            "revision_reason": "근로시간 변경에 따른 개정",
            "effective_date": "2026-07-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "draft"
    assert data["data"]["version"] == 2


@pytest.mark.asyncio
async def test_download_work_rule(client: AsyncClient, auth_token: str, company_id: str):
    """다운로드 테스트"""
    # 먼저 취업규칙 생성
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "manufacturing",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # DOCX 다운로드
    response = await client.get(
        f"/api/v1/work-rules/{work_rule_id}/download/docx",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "download_url" in data["data"]
    assert "filename" in data["data"]


@pytest.mark.asyncio
async def test_consent_checklist(client: AsyncClient, auth_token: str, company_id: str):
    """동의 절차 체크리스트 조회 테스트"""
    response = await client.get(
        "/api/v1/work-rules/consent-checklist",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "checklist" in data["data"]
    assert "employee_count" in data["data"]
    assert "consent_threshold" in data["data"]


@pytest.mark.asyncio
async def test_generate_cover_document(client: AsyncClient, auth_token: str, company_id: str):
    """신고용 커버 서류 생성 테스트"""
    # 먼저 취업규칙 생성 및 활성화
    create_response = await client.post(
        "/api/v1/work-rules/",
        json={
            "industry_type": "manufacturing",
            "effective_date": "2026-04-01"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    work_rule_id = create_response.json()["data"]["id"]

    # 상태를 active로 변경
    update_response = await client.put(
        f"/api/v1/work-rules/{work_rule_id}",
        json={"status": "active"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert update_response.status_code == 200

    # 커버 서류 생성
    response = await client.post(
        f"/api/v1/work-rules/{work_rule_id}/file",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "cover_document_url" in data["data"]
