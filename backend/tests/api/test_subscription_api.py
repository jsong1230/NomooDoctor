"""
F-11 구독 및 결제 — 통합 테스트
"""

import pytest
import random
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi import status


def generate_email():
    return f"test_sub_{random.randint(10000, 99999)}@example.com"


async def register_and_login(client, email=None, password="TestP@ss123", name="테스트사용자"):
    if email is None:
        email = generate_email()

    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": name}
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    if login_response.status_code == 200:
        data = login_response.json()
        return data.get("data", {}).get("access_token")
    return None


class TestSubscriptionPlansAPI:

    async def test_비인증_플랜_목록_조회_성공(self, client):
        response = await client.get("/api/v1/subscriptions/plans")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["plans"]) == 4

        plans = {p["id"]: p for p in data["data"]["plans"]}
        assert plans["starter"]["price"] == 0
        assert plans["basic"]["price"] == 9900
        assert plans["standard"]["price"] == 29000
        assert plans["premium"]["price"] == 49000

        assert plans["starter"]["features"]["chat_limit"] == 10
        assert plans["premium"]["features"]["attorney_consult"] is True


class TestMySubscriptionAPI:

    async def test_구독_없는_사용자_조회_성공(self, client):
        token = await register_and_login(client)
        assert token is not None

        response = await client.get(
            "/api/v1/subscriptions/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["subscription"] is None
        assert data["data"]["usage"]["chat_count"] == 0

    async def test_미인증_요청_실패(self, client):
        response = await client.get("/api/v1/subscriptions/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateSubscriptionAPI:
    """구독 생성 API - TossClient는 내장 mock 모드로 동작 (API key 미설정)"""

    async def test_구독_생성_성공_정기결제(self, client):
        token = await register_and_login(client)
        assert token is not None

        billing_key = f"tb_{uuid.uuid4()}"
        response = await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic", "billing_key": billing_key}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "subscription_id" in data["data"]
        assert data["data"]["status"] == "active"
        assert "starts_at" in data["data"]
        assert "expires_at" in data["data"]

    async def test_이미_활성_구독_존재_실패(self, client):
        token = await register_and_login(client)
        assert token is not None

        # 첫 번째 구독 생성
        await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic", "billing_key": f"tb_{uuid.uuid4()}"}
        )

        # 두 번째 구독 시도
        response = await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "standard", "billing_key": f"tb_{uuid.uuid4()}"}
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-7004"

    async def test_유효하지_않은_빌링키_실패(self, client):
        token = await register_and_login(client)
        assert token is not None

        response = await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic", "billing_key": "tb_invalid_key"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-7005"

    async def test_빌링키_없음_실패(self, client):
        token = await register_and_login(client)
        assert token is not None

        response = await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-1003"

    async def test_미인증_요청_실패(self, client):
        response = await client.post(
            "/api/v1/subscriptions",
            json={"plan": "basic", "billing_key": f"tb_{uuid.uuid4()}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestChangePlanAPI:

    async def test_업그레이드_성공_basic_to_standard(self, client):
        token = await register_and_login(client)
        assert token is not None

        # basic 구독 생성
        await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic", "billing_key": f"tb_{uuid.uuid4()}"}
        )

        # 업그레이드
        response = await client.put(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "standard"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["old_plan"] == "basic"
        assert data["data"]["new_plan"] == "standard"
        assert "proration_amount" in data["data"]
        assert data["data"]["next_billing_amount"] == 29000

    async def test_동일_플랜_변경_실패(self, client):
        token = await register_and_login(client)
        assert token is not None

        await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic", "billing_key": f"tb_{uuid.uuid4()}"}
        )

        response = await client.put(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic"}
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-7004"

    async def test_활성_구독_없음_실패(self, client):
        token = await register_and_login(client)
        assert token is not None

        response = await client.put(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "standard"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-7003"

    async def test_미인증_요청_실패(self, client):
        response = await client.put(
            "/api/v1/subscriptions",
            json={"plan": "standard"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCancelSubscriptionAPI:

    async def test_구독_해지_성공(self, client):
        token = await register_and_login(client)
        assert token is not None

        await client.post(
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic", "billing_key": f"tb_{uuid.uuid4()}"}
        )

        response = await client.request(
            "DELETE",
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={"reason": "사용 빈도 낮음", "feedback": "가격이 비싸요"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "cancelled"
        assert "cancelled_at" in data["data"]
        assert "access_until" in data["data"]

    async def test_이미_해지된_구독_실패(self, client):
        token = await register_and_login(client)
        assert token is not None

        response = await client.request(
            "DELETE",
            "/api/v1/subscriptions",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-7003"

    async def test_미인증_요청_실패(self, client):
        response = await client.delete("/api/v1/subscriptions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPaymentHistoryAPI:

    async def test_결제_내역_조회_성공(self, client):
        token = await register_and_login(client)
        assert token is not None

        response = await client.get(
            "/api/v1/subscriptions/history",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "payments" in data["data"]
        assert "pagination" in data["data"]

    async def test_미인증_요청_실패(self, client):
        response = await client.get("/api/v1/subscriptions/history")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTossWebhookAPI:

    async def test_결제_성공_웹훅_처리(self, client):
        payload = {
            "eventType": "PAYMENT_STATUS_CHANGED",
            "data": {
                "paymentId": f"pay_{uuid.uuid4()}",
                "orderId": f"order_{uuid.uuid4()}",
                "status": "DONE",
                "totalAmount": 9900
            }
        }

        response = await client.post(
            "/api/v1/webhooks/toss",
            json=payload,
            headers={"X-Toss-Signature": "valid_signature"}
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_잘못된_이벤트_타입_무시(self, client):
        payload = {"eventType": "UNKNOWN_EVENT", "data": {}}

        response = await client.post(
            "/api/v1/webhooks/toss",
            json=payload,
            headers={"X-Toss-Signature": "valid_signature"}
        )
        assert response.status_code == status.HTTP_200_OK
