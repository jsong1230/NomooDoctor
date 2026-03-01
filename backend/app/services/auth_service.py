# 인증 서비스
from typing import Optional, Any
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from jose.exceptions import JWTError, ExpiredSignatureError

from app.db.models.user import User
from app.repositories.user_repo import UserRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.core.exceptions import (
    ValidationError,
    UnauthorizedError,
    NotFoundError,
    RateLimitExceededError,
)


class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession, redis: aioredis.Redis) -> None:
        self.db = db
        self.repo = UserRepository(db)
        self.redis = redis

    async def register(
        self,
        email: str,
        password: str,
        name: str,
        phone: Optional[str] = None
    ) -> dict[str, Any]:
        """
        회원가입

        Args:
            email: 이메일
            password: 비밀번호
            name: 이름
            phone: 전화번호

        Returns:
            사용자 정보와 토큰

        Raises:
            ValidationError: 이메일 중복, 비밀번호 정책 위반
        """
        # 이메일 중복 확인
        existing_user = await self.repo.get_by_email(email)
        if existing_user:
            raise ValidationError(
                message="이미 등록된 이메일입니다.",
                details=[{"field": "email", "message": "이미 사용 중인 이메일입니다."}]
            )

        # 비밀번호 정책 검증 (최소 8자)
        if len(password) < 8:
            raise ValidationError(
                message="비밀번호는 8자 이상이어야 합니다.",
                details=[{"field": "password", "message": "최소 8자 이상 입력해주세요."}]
            )

        # 비밀번호 해싱
        hashed_password = hash_password(password)

        # 사용자 생성
        user = await self.repo.create(
            email=email,
            hashed_password=hashed_password,
            name=name,
            phone=phone,
            role="owner",
            plan="free"
        )

        # 토큰 생성
        tokens = await self._create_tokens(user)

        await self.db.commit()

        return {
            "user": self._user_to_dict(user),
            **tokens
        }

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """
        로그인

        Args:
            email: 이메일
            password: 비밀번호

        Returns:
            사용자 정보와 토큰

        Raises:
            UnauthorizedError: 비밀번호 불일치, 비활성 계정
            NotFoundError: 사용자 없음
        """
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다.")

        if not user.is_active:
            raise UnauthorizedError("비활성화된 계정입니다.")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("비밀번호가 일치하지 않습니다.")

        # 토큰 생성
        tokens = await self._create_tokens(user)

        return {
            "user": self._user_to_dict(user),
            **tokens
        }

    async def refresh(self, refresh_token: str) -> dict[str, Any]:
        """
        토큰 갱신 (Refresh Token Rotation)

        Args:
            refresh_token: 리프레시 토큰

        Returns:
            새 액세스 토큰과 리프레시 토큰

        Raises:
            UnauthorizedError: 유효하지 않은 토큰, 만료된 토큰, 재사용 감지
        """
        # rt_ 접두사 제거
        token_value = refresh_token[3:] if refresh_token.startswith("rt_") else refresh_token

        # 토큰 디코딩
        try:
            payload = decode_token(refresh_token)
        except (ExpiredSignatureError, JWTError):
            raise UnauthorizedError("유효하지 않은 리프레시 토큰입니다.")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("토큰에 사용자 정보가 없습니다.")

        # Redis에서 저장된 토큰 확인
        stored_token = await self.redis.get(f"refresh:{user_id}")

        # 재사용 감지 (저장된 토큰과 일치하지 않음)
        if stored_token and stored_token != token_value:
            # 보안: 모든 토큰 삭제 (탈취 의심)
            await self.redis.delete(f"refresh:{user_id}")
            raise UnauthorizedError("토큰이 만료되었습니다. 다시 로그인해주세요.")

        if not stored_token:
            raise UnauthorizedError("리프레시 토큰이 만료되었습니다.")

        # 사용자 확인
        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            await self.redis.delete(f"refresh:{user_id}")
            raise UnauthorizedError("유효하지 않은 사용자입니다.")

        # 새 토큰 생성 (Rotation)
        tokens = await self._create_tokens(user)

        return tokens

    async def logout(self, user_id: str, token_jti: str) -> None:
        """
        로그아웃

        Args:
            user_id: 사용자 ID
            token_jti: 액세스 토큰의 jti
        """
        # Refresh Token 삭제
        await self.redis.delete(f"refresh:{user_id}")

        # Access Token 블랙리스트 등록 (만료 시간까지)
        # jti에서 exp 추출 (필요한 경우)
        await self.redis.setex(f"blacklist:{token_jti}", 3600, "1")

    async def _create_tokens(self, user: User) -> dict[str, Any]:
        """
        토큰 생성 (Access + Refresh)

        Args:
            user: 사용자 모델

        Returns:
            액세스 토큰, 리프레시 토큰, 토큰 타입, 만료 시간
        """
        access_token = create_access_token(
            user_id=str(user.id),
            plan=user.plan,
            role=user.role
        )

        refresh_token = create_refresh_token(str(user.id))

        # Refresh Token Redis 저장 (30일 TTL)
        token_value = refresh_token[3:]  # rt_ 접두사 제거
        await self.redis.setex(
            f"refresh:{user.id}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            token_value
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def _user_to_dict(self, user: User) -> dict[str, Any]:
        """User 모델을 딕셔너리로 변환"""
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at.isoformat() if user.plan_expires_at else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
