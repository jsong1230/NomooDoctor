# 사용자 서비스
from typing import Optional, Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password, verify_password
from app.core.exceptions import ValidationError, NotFoundError


class UserService:
    """사용자 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = UserRepository(db)

    async def get_me(self, user: User) -> dict[str, Any]:
        """
        현재 사용자 정보 조회

        Args:
            user: 현재 로그인한 사용자

        Returns:
            사용자 정보
        """
        return self._user_to_dict(user)

    async def update_me(
        self,
        user: User,
        name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> dict[str, Any]:
        """
        현재 사용자 정보 수정

        Args:
            user: 현재 로그인한 사용자
            name: 새 이름
            phone: 새 전화번호

        Returns:
            수정된 사용자 정보
        """
        updated_user = await self.repo.update(user, name=name, phone=phone)
        await self.db.commit()

        return self._user_to_dict(updated_user)

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        비밀번호 변경

        Args:
            user: 현재 로그인한 사용자
            current_password: 현재 비밀번호
            new_password: 새 비밀번호

        Raises:
            ValidationError: 현재 비밀번호 불일치, 새 비밀번호 정책 위반
        """
        # 현재 비밀번호 검증
        if not verify_password(current_password, user.hashed_password):
            raise ValidationError(
                message="현재 비밀번호가 일치하지 않습니다.",
                details=[{"field": "current_password", "message": "비밀번호를 확인해주세요."}]
            )

        # 새 비밀번호 정책 검증
        if len(new_password) < 8:
            raise ValidationError(
                message="비밀번호는 8자 이상이어야 합니다.",
                details=[{"field": "new_password", "message": "최소 8자 이상 입력해주세요."}]
            )

        # 비밀번호 변경
        hashed_password = hash_password(new_password)
        await self.repo.update_password(user, hashed_password)
        await self.db.commit()

    async def delete_me(self, user: User, password: str) -> None:
        """
        계정 탈퇴 (Soft Delete)

        Args:
            user: 현재 로그인한 사용자
            password: 비밀번호 확인

        Raises:
            ValidationError: 비밀번호 불일치
        """
        # 비밀번호 검증
        if not verify_password(password, user.hashed_password):
            raise ValidationError(
                message="비밀번호가 일치하지 않습니다.",
                details=[{"field": "password", "message": "비밀번호를 확인해주세요."}]
            )

        # 비활성화 (Soft Delete)
        await self.repo.deactivate(user)
        await self.db.commit()

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
