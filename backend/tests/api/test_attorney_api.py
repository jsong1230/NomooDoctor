"""
F-12 노무사 마켓플레이스 — 통합 테스트
"""

import pytest
import random
import uuid
from fastapi import status


def generate_email():
    return f"test_atty_{random.randint(10000, 99999)}@example.com"


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


async def create_test_attorney(db):
    """테스트용 노무사 생성 (DB 직접 삽입)"""
    from app.db.models.attorney import LaborAttorney
    from app.db.models.user import User
    from datetime import datetime, timezone

    # 노무사 유저 생성
    user = User(
        email=f"attorney_{random.randint(10000,99999)}@example.com",
        hashed_password="$2b$12$dummy_hash",
        name="김노무사",
        role="attorney",
        plan="free",
        is_active=True,
    )
    db.add(user)
    await db.flush()

    attorney = LaborAttorney(
        user_id=user.id,
        license_number=f"LIC-{random.randint(10000,99999)}",
        name="김노무사",
        firm_name="테스트 노무법인",
        specialties=["dismissal", "wage"],
        regions=["서울", "경기"],
        consultation_fee=50000,
        experience_years=10,
        rating=4.5,
        review_count=0,
        response_rate=95,
        bio="10년 경력 노무사입니다.",
        verified=True,
        is_active=True,
    )
    db.add(attorney)
    await db.commit()
    await db.refresh(attorney)
    return attorney


class TestAttorneyListAPI:

    async def test_노무사_목록_조회_성공(self, client, db):
        attorney = await create_test_attorney(db)

        response = await client.get("/api/v1/attorneys")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "attorneys" in data["data"]
        assert data["data"]["total_count"] >= 1

    async def test_노무사_목록_필터_조회_성공(self, client, db):
        attorney = await create_test_attorney(db)

        response = await client.get(
            "/api/v1/attorneys",
            params={"specialty": "dismissal", "region": "서울"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

    async def test_노무사_상세_조회_성공(self, client, db):
        attorney = await create_test_attorney(db)

        response = await client.get(f"/api/v1/attorneys/{attorney.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["attorney"]["name"] == "김노무사"
        assert "recent_reviews" in data["data"]


class TestCaseAPI:

    async def test_상담_신청_성공(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        response = await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "dismissal",
                "urgency": "high",
                "consultation_type": "video",
                "description": "부당해고 관련 상담 요청"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "case_id" in data["data"]
        assert data["data"]["status"] == "pending"

    async def test_상담_신청_미인증_실패(self, client, db):
        attorney = await create_test_attorney(db)
        response = await client.post(
            "/api/v1/attorney-cases",
            json={
                "attorney_id": str(attorney.id),
                "case_type": "wage",
                "urgency": "medium",
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_내_케이스_목록_조회_성공(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        # 케이스 생성
        await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "wage",
                "urgency": "low",
                "description": "임금 관련 문의"
            }
        )

        response = await client.get(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["cases"]) >= 1

    async def test_케이스_상세_조회_성공(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        create_resp = await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "harassment",
                "urgency": "high",
                "description": "직장 내 괴롭힘 상담"
            }
        )
        case_id = create_resp.json()["data"]["case_id"]

        response = await client.get(
            f"/api/v1/attorney-cases/{case_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["case_type"] == "harassment"

    async def test_케이스_취소_성공(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        create_resp = await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "leave",
                "urgency": "low",
                "description": "휴가 관련"
            }
        )
        case_id = create_resp.json()["data"]["case_id"]

        response = await client.put(
            f"/api/v1/attorney-cases/{case_id}/cancel",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["status"] == "cancelled"

    async def test_존재하지_않는_케이스_실패(self, client):
        token = await register_and_login(client)
        assert token is not None
        fake_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/attorney-cases/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReviewAPI:

    async def test_리뷰_작성_성공(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        # 케이스 생성
        create_resp = await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "other",
                "urgency": "low",
                "description": "일반 상담"
            }
        )
        case_id = create_resp.json()["data"]["case_id"]

        # 리뷰 작성
        response = await client.post(
            f"/api/v1/attorney-cases/{case_id}/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"rating": 5, "comment": "매우 친절하고 전문적입니다."}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "review_id" in data["data"]

    async def test_리뷰_중복_작성_실패(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        create_resp = await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "wage",
                "urgency": "low",
                "description": "임금 상담"
            }
        )
        case_id = create_resp.json()["data"]["case_id"]

        # 첫 번째 리뷰
        await client.post(
            f"/api/v1/attorney-cases/{case_id}/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"rating": 4, "comment": "좋아요"}
        )

        # 두 번째 리뷰 시도
        response = await client.post(
            f"/api/v1/attorney-cases/{case_id}/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"rating": 3, "comment": "다시 리뷰"}
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["error"]["code"] == "E-8003"

    async def test_노무사_리뷰_목록_조회(self, client, db):
        token = await register_and_login(client)
        assert token is not None
        attorney = await create_test_attorney(db)

        # 케이스 + 리뷰 생성
        create_resp = await client.post(
            "/api/v1/attorney-cases",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "attorney_id": str(attorney.id),
                "case_type": "other",
                "urgency": "low",
                "description": "일반"
            }
        )
        case_id = create_resp.json()["data"]["case_id"]
        await client.post(
            f"/api/v1/attorney-cases/{case_id}/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"rating": 5, "comment": "훌륭합니다"}
        )

        # 리뷰 목록 조회
        response = await client.get(f"/api/v1/attorneys/{attorney.id}/reviews")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["reviews"]) >= 1
