# Rate Limiting 모듈
from fastapi import HTTPException, Request, status
from redis import asyncio as aioredis

from app.core.config import settings


async def get_redis() -> aioredis.Redis:
    """Redis 인스턴스 반환"""
    redis = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    return redis


async def check_rate_limit(
    redis: aioredis.Redis,
    key: str,
    limit: int,
    window_seconds: int
) -> None:
    """
    Rate Limit 체크

    Args:
        redis: Redis 인스턴스
        key: Rate Limit 키 (예: ratelimit:login:192.168.1.1)
        limit: 제한 횟수
        window_seconds: 윈도우 크기 (초)

    Raises:
        HTTPException: Rate Limit 초과 시 (429)
    """
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window_seconds)

    if current > limit:
        ttl = await redis.ttl(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "E-2006",
                "message": f"요청 횟수를 초과했습니다. {ttl}초 후 다시 시도해주세요.",
                "details": {
                    "retry_after": ttl,
                    "limit": limit
                }
            }
        )


async def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


async def create_oauth_state(redis: aioredis.Redis, user_ip: str) -> str:
    """
    OAuth state 생성

    Args:
        redis: Redis 인스턴스
        user_ip: 사용자 IP

    Returns:
        생성된 state 문자열
    """
    import secrets
    state = secrets.token_urlsafe(32)
    key = f"oauth_state:{state}"
    await redis.setex(key, 600, user_ip)  # 10분 유효
    return state


async def verify_oauth_state(redis: aioredis.Redis, state: str, user_ip: str) -> bool:
    """
    OAuth state 검증

    Args:
        redis: Redis 인스턴스
        state: 검증할 state 값
        user_ip: 사용자 IP

    Returns:
        검증 성공 여부
    """
    key = f"oauth_state:{state}"
    stored_ip = await redis.get(key)

    if stored_ip and stored_ip == user_ip:
        await redis.delete(key)
        return True

    return False
