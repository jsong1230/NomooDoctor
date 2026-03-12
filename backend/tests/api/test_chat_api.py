# Chat API 테스트
import pytest
from httpx import AsyncClient


@pytest.fixture
async def setup_chat_user(client: AsyncClient):
    """채팅 테스트용 사용자 및 사업장 설정"""
    import random
    suffix = random.randint(10000, 99999)

    # 사용자 등록
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"chat_test_{suffix}@example.com",
            "password": "TestP@ss123",
            "name": "채팅테스트",
        },
    )

    # 로그인
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": f"chat_test_{suffix}@example.com",
            "password": "TestP@ss123",
        },
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 사업장 등록
    company_resp = await client.post(
        "/api/v1/companies/",
        json={
            "business_name": f"채팅테스트사업장_{suffix}",
            "business_number": f"{suffix % 1000:03d}-{suffix % 100:02d}-{suffix:05d}",
            "representative_name": "테스트대표",
            "industry_type": "it",
            "employee_count": 5,
        },
        headers=headers,
    )
    assert company_resp.status_code == 201, f"Company create failed: {company_resp.text}"
    company_id = company_resp.json()["data"]["id"]

    # 사업장 선택 (company_id를 JWT에 포함)
    select_resp = await client.post(
        f"/api/v1/companies/{company_id}/select",
        headers=headers,
    )
    assert select_resp.status_code == 200, f"Company select failed: {select_resp.text}"
    new_token = select_resp.json().get("data", {}).get("access_token")
    if new_token:
        headers = {"Authorization": f"Bearer {new_token}"}

    return {"headers": headers, "company_id": company_id}


class TestChatSessions:
    """채팅 세션 CRUD 테스트"""

    @pytest.mark.asyncio
    async def test_세션_생성_성공(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        response = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "최저임금 관련 질문"},
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "최저임금 관련 질문"
        assert data["data"]["risk_level"] == "low"
        assert data["data"]["message_count"] == 0

    @pytest.mark.asyncio
    async def test_세션_목록_조회(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        # 세션 2개 생성
        await client.post(
            "/api/v1/chat/sessions",
            json={"title": "첫 번째 질문"},
            headers=headers,
        )
        await client.post(
            "/api/v1/chat/sessions",
            json={"title": "두 번째 질문"},
            headers=headers,
        )

        response = await client.get(
            "/api/v1/chat/sessions",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 2

    @pytest.mark.asyncio
    async def test_세션_상세_조회(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        # 세션 생성
        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "상세 조회 테스트"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        response = await client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session"]["id"] == session_id
        assert data["data"]["messages"] == []

    @pytest.mark.asyncio
    async def test_세션_삭제(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        # 세션 생성
        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "삭제될 세션"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        # 삭제
        response = await client.delete(
            f"/api/v1/chat/sessions/{session_id}",
            headers=headers,
        )
        assert response.status_code == 204

        # 삭제 확인
        get_resp = await client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers=headers,
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_존재하지_않는_세션_조회_404(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        response = await client.get(
            "/api/v1/chat/sessions/00000000-0000-0000-0000-000000000000",
            headers=headers,
        )
        assert response.status_code == 404


class TestChatMessages:
    """채팅 메시지 전송 테스트 (SSE)"""

    @pytest.mark.asyncio
    async def test_메시지_전송_SSE_응답(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        # 세션 생성
        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "메시지 테스트"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        # 메시지 전송 (SSE 스트리밍)
        response = await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": "최저임금이 얼마인가요?"},
            headers=headers,
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        # SSE 이벤트 파싱
        body = response.text
        assert "event: message" in body or "event: done" in body or "event: error" in body

    @pytest.mark.asyncio
    async def test_메시지_전송_후_세션_메시지_저장(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        # 세션 생성
        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "저장 테스트"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        # 메시지 전송
        await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": "연차휴가 계산법을 알려주세요."},
            headers=headers,
        )

        # 세션 상세 조회하여 메시지 확인
        detail_resp = await client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers=headers,
        )

        data = detail_resp.json()
        messages = data["data"]["messages"]
        assert len(messages) >= 1  # 최소 사용자 메시지 1개

        # 사용자 메시지 확인
        user_messages = [m for m in messages if m["role"] == "user"]
        assert len(user_messages) >= 1
        assert "연차" in user_messages[0]["content"]

    @pytest.mark.asyncio
    async def test_빈_메시지_전송_실패(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "빈 메시지 테스트"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": ""},
            headers=headers,
        )

        assert response.status_code in (400, 422)


class TestChatFAQ:
    """FAQ 테스트"""

    @pytest.mark.asyncio
    async def test_FAQ_목록_조회(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        response = await client.get(
            "/api/v1/chat/faq",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 5

        # 카테고리 확인
        categories = [item["category"] for item in data["data"]]
        assert "임금" in categories
        assert "해고" in categories
        assert "휴가" in categories


class TestChatRiskClassification:
    """위험도 분류 테스트"""

    @pytest.mark.asyncio
    async def test_해고_질문_HIGH_위험도(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "해고 관련 질문"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": "직원을 해고하고 싶은데 어떻게 해야 하나요?"},
            headers=headers,
        )

        body = response.text
        # SSE 이벤트에 risk_level 포함 확인
        assert "event: risk_level" in body

    @pytest.mark.asyncio
    async def test_면책_문구_포함_확인(self, client: AsyncClient, setup_chat_user):
        headers = setup_chat_user["headers"]

        create_resp = await client.post(
            "/api/v1/chat/sessions",
            json={"title": "면책 문구 테스트"},
            headers=headers,
        )
        session_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": "최저임금은 얼마인가요?"},
            headers=headers,
        )

        body = response.text
        # SSE 응답에 면책 문구 포함 확인
        assert "면책 고지" in body
