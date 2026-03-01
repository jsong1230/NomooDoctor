"""
F-01 사용자 인증 — 단위 테스트 (RED)

이 파일은 구현 전 실패하는 테스트입니다.
실제 구현은 backend-dev 에이전트가 수행합니다.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import JWTError, ExpiredSignatureError
from unittest.mock import AsyncMock

# 테스트 대상 모듈
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.rate_limit import (
    check_rate_limit,
    create_oauth_state,
    verify_oauth_state,
)



class TestPasswordHashing:
    """비밀번호 해싱 및 검증 테스트"""

    def test_비밀번호_해싱_성공(self):
        """일반 비밀번호를 해싱하면 bcrypt 해시 문자열(60자)가 반환되어야 함"""
        password = "SecureP@ss123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) == 60
        assert hashed.startswith("$2b$12$")

    def test_동일_비밀번호_다른_해시(self):
        """동일한 비밀번호를 해싱하면 salt로 인해 서로 다른 해시가 생성되어야 함"""
        password = "SecureP@ss123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_올바른_비밀번호_검증_성공(self):
        """올바른 비밀번호는 해시와 일치해야 함"""
        password = "SecureP@ss123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_잘못된_비밀번호_검증_실패(self):
        """잘못된 비밀번호는 해시와 일치하지 않아야 함"""
        password = "SecureP@ss123"
        hashed = hash_password(password)
        wrong_password = "WrongP@ss"

        assert verify_password(wrong_password, hashed) is False

    def test_빈_비밀번호_검증_실패(self):
        """빈 비밀번호는 검증에 실패해야 함"""
        password = "SecureP@ss123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False


class TestJWTCreation:
    """JWT 생성 테스트"""

    def test_액세스_토큰_생성_성공(self):
        """정상적인 파라미터로 액세스 토큰이 생성되어야 함"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        company_id = "660e8400-e29b-41d4-a716-446655440001"
        plan = "standard"
        role = "owner"

        token = create_access_token(
            user_id=user_id,
            company_id=company_id,
            plan=plan,
            role=role
        )

        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT 구조: header.payload.signature

    def test_토큰_만료시간_1시간(self):
        """액세스 토큰은 설정된 만료 시간 후 만료되어야 함"""
        from app.core.config import settings
        import time
        from datetime import timezone

        # 토큰 생성
        token = create_access_token(
            user_id="test-id",
            company_id="company-id",
            plan="free",
            role="owner"
        )

        payload = decode_token(token)
        exp = payload.get("exp")

        # 만료 시간이 현재 시간으로부터 ACCESS_TOKEN_EXPIRE_MINUTES 후여야 함
        # time.time()을 사용하여 현재 UTC timestamp 가져옴
        now_timestamp = int(time.time())
        expected_exp_seconds = now_timestamp + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        time_diff = abs(exp - expected_exp_seconds)

        # 10초 이내 오차 허용
        assert time_diff < 10

    def test_리프레시_토큰_생성_성공(self):
        """정상적인 파라미터로 리프레시 토큰이 생성되어야 함"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"

        token = create_refresh_token(user_id)

        assert isinstance(token, str)
        assert token.startswith("rt_")
        assert len(token) > 10

    def test_리프레시_토큰만료시간_30일(self):
        """리프레시 토큰은 30일 후 만료되어야 함"""
        user_id = "test-id"
        token = create_refresh_token(user_id)

        # Redis에 저장된 토큰의 TTL을 확인
        # 이 테스트는 통합 테스트에서 Redis를 확인


class TestJWTDecoding:
    """JWT 디코딩 테스트"""

    def test_유효한_토큰_디코딩_성공(self):
        """유효한 토큰을 디코딩하면 payload가 반환되어야 함"""
        token = create_access_token(
            user_id="test-id",
            company_id="company-id",
            plan="standard",
            role="owner"
        )

        payload = decode_token(token)

        assert payload.get("sub") == "test-id"
        assert payload.get("company_id") == "company-id"
        assert payload.get("plan") == "standard"
        assert payload.get("role") == "owner"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload

    def test_만료된_토큰_디코딩_실패(self):
        """만료된 토큰을 디코딩하면 ExpiredSignatureError가 발생해야 함"""
        # 만료된 토큰 생성 (과거 시간)
        user_id = "test-id"
        company_id = "company-id"
        plan = "free"
        role = "owner"
        expire_delta = timedelta(hours=-1)

        token = create_access_token(
            user_id=user_id,
            company_id=company_id,
            plan=plan,
            role=role,
            expire_delta=expire_delta
        )

        with pytest.raises(ExpiredSignatureError):
            decode_token(token)

    def test_변조된_토큰_디코딩_실패(self):
        """서명이 변조된 토큰은 JWTError가 발생해야 함"""
        token = create_access_token(
            user_id="test-id",
            company_id="company-id",
            plan="free",
            role="owner"
        )

        # 토큰 변조
        parts = token.split(".")
        parts[1] += "tampered"
        tampered_token = ".".join(parts)

        with pytest.raises(JWTError):
            decode_token(tampered_token)

    def test_잘못된_형식_토큰_디코딩_실패(self):
        """잘못된 형식의 토큰은 JWTError가 발생해야 함"""
        invalid_tokens = [
            "invalid.token",
            "invalid.token.format",
            "",
            "not-a-jwt"
        ]

        for token in invalid_tokens:
            with pytest.raises(JWTError):
                decode_token(token)


class TestRateLimiting:
    """Rate Limiting 테스트"""

    @pytest.fixture
    async def mock_redis(self):
        """Mock Redis 인스턴스"""
        redis = AsyncMock()
        redis.incr.return_value = 1
        redis.expire.return_value = None
        redis.ttl.return_value = 60
        return redis

    async def test_제한_내_요청_통과(self, mock_redis):
        """제한 내의 요청은 정상적으로 통과해야 함"""
        mock_redis.incr.return_value = 3

        # 5회 제한 중 3회 요청
        await check_rate_limit(
            redis=mock_redis,
            key="ratelimit:login:192.168.1.1",
            limit=5,
            window_seconds=60
        )
        # 예외 없이 통과

    async def test_제한_초과_요청_실패(self, mock_redis):
        """제한을 초과한 요청은 HTTPException(429)이 발생해야 함"""
        mock_redis.incr.return_value = 6
        mock_redis.ttl.return_value = 45

        with pytest.raises(HTTPException) as exc_info:
            await check_rate_limit(
                redis=mock_redis,
                key="ratelimit:login:192.168.1.1",
                limit=5,
                window_seconds=60
            )

        assert exc_info.value.status_code == 429
        assert "E-2006" in exc_info.value.detail.get("code", "")

    async def test_TTL_만료_후_재요청_통과(self, mock_redis):
        """TTL 만료 후 요청은 카운터가 리셋되어 통과해야 함"""
        # 처음 요청 (카운터 1)
        mock_redis.incr.return_value = 1

        await check_rate_limit(
            redis=mock_redis,
            key="ratelimit:login:192.168.1.1",
            limit=5,
            window_seconds=60
        )

        # TTL 만료 후 재요청 (새로운 카운터)
        mock_redis.incr.return_value = 1

        await check_rate_limit(
            redis=mock_redis,
            key="ratelimit:login:192.168.1.1",
            limit=5,
            window_seconds=60
        )


class TestOAuthState:
    """OAuth State 생성 및 검증 테스트"""

    async def test_oauth_state_생성_성공(self):
        """OAuth state가 올바르게 생성되어야 함"""
        user_ip = "192.168.1.1"
        redis = AsyncMock()
        redis.setex.return_value = None

        state = await create_oauth_state(redis, user_ip)

        assert isinstance(state, str)
        assert len(state) == 43  # 32바이트 URL-safe 토큰은 보통 43자

    async def test_유효한_state_검증_성공(self):
        """유효한 state와 일치하는 IP는 검증에 성공해야 함"""
        user_ip = "192.168.1.1"
        redis = AsyncMock()
        redis.get.return_value = user_ip  # decode_responses=True로 이미 디코딩됨

        state = "valid_state_token_12345"
        redis.setex.return_value = None

        result = await verify_oauth_state(redis, state, user_ip)

        assert result is True
        redis.delete.assert_called_once()

    async def test_만료된_state_검증_실패(self):
        """만료된 state는 검증에 실패해야 함"""
        user_ip = "192.168.1.1"
        redis = AsyncMock()
        redis.get.return_value = None  # 만료로 인해 없음

        state = "expired_state_token"
        result = await verify_oauth_state(redis, state, user_ip)

        assert result is False

    async def test_다른_IP_state_검증_실패(self):
        """다른 IP에서의 state는 검증에 실패해야 함"""
        redis = AsyncMock()
        redis.get.return_value = "192.168.1.1"  # decode_responses=True로 이미 디코딩됨

        state = "state_token"
        user_ip = "192.168.1.2"
        result = await verify_oauth_state(redis, state, user_ip)

        assert result is False


