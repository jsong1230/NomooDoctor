"""
F-01 사용자 인증 — 통합 테스트 (RED)

이 파일은 구현 전 실패하는 테스트입니다.
실제 구현은 backend-dev 에이전트가 수행합니다.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from fastapi import status

# 테스트 대상 앱 (아직 구현되지 않음)
# from app.main import app
from unittest.mock import MagicMock


class TestRegisterAPI:
    """회원가입 API 테스트"""

    @pytest.fixture
    async def client(self):
        """테스트용 AsyncClient"""
        app = MagicMock()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_정상_회원가입_성공(self, client):
        """정상적인 정보로 회원가입 요청 시 201과 함께 사용자와 토큰이 반환되어야 함"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestP@ss123",
                "name": "테스트사용자",
                "phone": "010-1234-5678"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "user" in data["data"]
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["expires_in"] == 3600
        assert data["data"]["user"]["email"] == "test@example.com"
        assert data["data"]["user"]["name"] == "테스트사용자"
        assert data["data"]["user"]["role"] == "owner"
        assert data["data"]["user"]["plan"] == "free"

    async def test_중복_이메일_회원가입_실패(self, client):
        """이미 등록된 이메일로 회원가입 시 409와 E-3001 에러가 반환되어야 함"""
        # 첫 번째 회원가입 (성공)
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "TestP@ss123",
                "name": "기존사용자",
                "phone": "010-1234-5678"
            }
        )

        # 중복 이메일로 시도
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "NewP@ss456",
                "name": "새사용자",
                "phone": "010-9876-5432"
            }
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-3001"

    async def test_잘못된_이메일_형식_회원가입_실패(self, client):
        """잘못된 이메일 형식으로 회원가입 시 400과 E-1001 에러가 반환되어야 함"""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@example.com",
            "a b@example.com",
            ""
        ]

        for email in invalid_emails:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "TestP@ss123",
                    "name": "테스트사용자",
                    "phone": "010-1234-5678"
                }
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["success"] is False
            assert data["error"]["code"] == "E-1001"

    async def test_비밀번호_정책_위반_회원가입_실패(self, client):
        """비밀번호 정책을 위반하는 경우 400과 E-1001 에러가 반환되어야 함"""
        weak_passwords = [
            "short1!",           # 8자 미만
            "alllowercase123",    # 대문자 없음
            "ALLUPPERCASE123",   # 소문자 없음
            "NoDigitsHere!",     # 숫자 없음
            "NoSpecialChar123"   # 특수문자 없음
        ]

        for password in weak_passwords:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": password,
                    "name": "테스트사용자",
                    "phone": "010-1234-5678"
                }
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert data["success"] is False
            assert data["error"]["code"] == "E-1001"

    async def test_필수_필드_누락_회원가입_실패(self, client):
        """필수 필드가 누락된 경우 400과 E-1003 에러가 반환되어야 함"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com"
                # password, name, phone 누락
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-1003"


class TestLoginAPI:
    """로그인 API 테스트"""

    @pytest.fixture
    async def client(self):
        """테스트용 AsyncClient"""
        app = MagicMock()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_정상_로그인_성공(self, client):
        """정상적인 로그인 요청 시 200과 함께 사용자와 토큰이 반환되어야 함"""
        # 먼저 회원가입
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "TestP@ss123",
                "name": "로그인사용자",
                "phone": "010-1234-5678"
            }
        )

        # 로그인
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "TestP@ss123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "user" in data["data"]
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["email"] == "login@example.com"

    async def test_존재하지_않는_이메일_로그인_실패(self, client):
        """존재하지 않는 이메일로 로그인 시 404와 E-3002 에러가 반환되어야 함"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestP@ss123"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-3002"

    async def test_비밀번호_불일치_로그인_실패(self, client):
        """비밀번호가 일치하지 않으면 401과 E-3003 에러가 반환되어야 함"""
        # 먼저 회원가입
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "TestP@ss123",
                "name": "사용자",
                "phone": "010-1234-5678"
            }
        )

        # 잘못된 비밀번호로 로그인
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongP@ss456"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-3003"

    async def test_비활성_계정_로그인_실패(self, client):
        """비활성화된 계정으로 로그인 시 401과 E-3004 에러가 반환되어야 함"""
        # 비활성 계정으로 회원가입 (DB에서 is_active=False)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "TestP@ss123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-3004"


class TestRefreshTokenAPI:
    """토큰 갱신 API 테스트"""

    @pytest.fixture
    async def client(self):
        """테스트용 AsyncClient"""
        app = MagicMock()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_정상_토큰_갱신_성공(self, client):
        """유효한 리프레시 토큰으로 갱신 시 200과 새 토큰이 반환되어야 함"""
        # 먼저 로그인
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "refresh@example.com",
                "password": "TestP@ss123"
            }
        )
        refresh_token = login_response.json()["data"]["refresh_token"]

        # 토큰 갱신
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh_token
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        # 새 토큰은 이전 토큰과 달라야 함 (Rotation)
        assert data["data"]["refresh_token"] != refresh_token

    async def test_만료된_리프레시_토큰_갱신_실패(self, client):
        """만료된 리프레시 토큰으로 갱신 시 401과 E-2002 에러가 반환되어야 함"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "rt_expired_token_here"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-2002"

    async def test_잘못된_리프레시_토큰_갱신_실패(self, client):
        """잘못된 형식의 리프레시 토큰으로 갱신 시 401과 E-2004 에러가 반환되어야 함"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid_token"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-2004"

    async def test_재사용_감지_토큰_갱신_실패(self, client):
        """이미 사용된 리프레시 토큰 재사용 시 401과 E-2004 에러가 반환되어야 함"""
        # 로그인
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "reuse@example.com",
                "password": "TestP@ss123"
            }
        )
        old_refresh_token = login_response.json()["data"]["refresh_token"]

        # 첫 번째 갱신 (성공)
        await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": old_refresh_token
            }
        )

        # 이전 토큰 재사용 시도 (실패 - 탈취 감지)
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": old_refresh_token
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-2004"


class TestLogoutAPI:
    """로그아웃 API 테스트"""

    @pytest.fixture
    async def client(self):
        """테스트용 AsyncClient"""
        app = MagicMock()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_정상_로그아웃_성공(self, client):
        """정상 로그아웃 시 200과 함께 토큰이 무효화되어야 함"""
        # 로그인
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "logout@example.com",
                "password": "TestP@ss123"
            }
        )
        access_token = login_response.json()["data"]["access_token"]

        # 로그아웃
        response = await client.post(
            "/api/v1/auth/logout",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "로그아웃되었습니다."

    async def test_인증_없이_로그아웃_요청_실패(self, client):
        """인증 없이 로그아웃 요청 시 401과 E-2001 에러가 반환되어야 함"""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E-2001"

    async def test_로그아웃된_토큰으로_접근_실패(self, client):
        """로그아웃된 토큰으로 보호된 API 접근 시 401이 반환되어야 함"""
        # 로그인
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "blacklist@example.com",
                "password": "TestP@ss123"
            }
        )
        access_token = login_response.json()["data"]["access_token"]

        # 로그아웃
        await client.post(
            "/api/v1/auth/logout",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        # 로그아웃된 토큰으로 API 접근 시도
        response = await client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
