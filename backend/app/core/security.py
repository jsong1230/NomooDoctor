# 보안 관련 유틸리티 (JWT, 비밀번호 해싱, 암호화)
from datetime import datetime, timedelta, timezone
from typing import Any
import calendar

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 비밀번호 해싱 (bcrypt rounds=12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해시 생성 (호환성용)"""
    return hash_password(password)


def _get_utc_timestamp(dt: datetime) -> int:
    """
    정확한 UTC timestamp 반환 (시간대 영향 없이)

    Args:
        dt: datetime 객체 (UTC로 가정)

    Returns:
        UTC timestamp (초 단위 int)
    """
    # calendar.timegm을 사용하여 UTC timestamp 정확하게 계산
    return calendar.timegm(dt.utctimetuple())


def create_access_token(
    user_id: str,
    company_id: str | None = None,
    plan: str = "free",
    role: str = "owner",
    expire_delta: timedelta | None = None
) -> str:
    """
    Access Token 생성

    Args:
        user_id: 사용자 ID
        company_id: 사업장 ID (선택)
        plan: 구독 플랜
        role: 사용자 역할
        expire_delta: 만료 시간 델타 (기본: 1시간)

    Returns:
        JWT Access Token
    """
    if expire_delta is None:
        expire_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    iat = datetime.now(timezone.utc)
    expire = iat + expire_delta
    jti = str(__import__("uuid").uuid4())

    to_encode: dict[str, Any] = {
        "exp": _get_utc_timestamp(expire),
        "iat": _get_utc_timestamp(iat),
        "jti": jti,
        "sub": user_id,
        "plan": plan,
        "role": role,
    }

    if company_id:
        to_encode["company_id"] = company_id

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Refresh Token 생성

    Args:
        user_id: 사용자 ID

    Returns:
        rt_ 접두사가 있는 JWT Refresh Token
    """
    iat = datetime.now(timezone.utc)
    expire = iat + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(__import__("uuid").uuid4())

    to_encode = {
        "exp": _get_utc_timestamp(expire),
        "iat": _get_utc_timestamp(iat),
        "jti": jti,
        "sub": user_id,
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return f"rt_{encoded_jwt}"


def decode_token(token: str) -> dict[str, Any]:
    """
    토큰 디코딩

    Args:
        token: JWT 토큰

    Returns:
        토큰 payload

    Raises:
        ExpiredSignatureError: 만료된 토큰
        JWTError: 유효하지 않은 토큰
    """
    # rt_ 접두사 제거
    if token.startswith("rt_"):
        token = token[3:]

    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload
