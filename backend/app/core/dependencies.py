"""공통 의존성 (FastAPI Depends)"""
from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_token
from app.db.session import get_db
from app.db.models.user import User
from app.core.exceptions import UnauthorizedError, ForbiddenError


security = HTTPBearer()


async def get_redis():
    """Redis 의존성"""
    from app.core.rate_limit import get_redis
    return await get_redis()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    현재 로그인한 사용자 ID 반환 (DB 조회 없이 JWT에서만)
    """
    from jose.exceptions import JWTError

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedError("유효하지 않은 토큰입니다.")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("토큰에 사용자 정보가 없습니다.")

    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    현재 로그인한 사용자 정보 반환 (DB 조회 포함)
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("존재하지 않는 사용자입니다.")

    if not user.is_active:
        raise ForbiddenError("비활성화된 계정입니다.")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """현재 활성 사용자 반환 (이미 is_active 체크됨)"""
    return current_user


def get_request_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.client.host if request.client else "unknown"

