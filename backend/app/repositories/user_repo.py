# User Repository
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models.user import User


class UserRepository:
    """User CRUD 작업을 담당하는 Repository"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID | str) -> Optional[User]:
        """ID로 사용자 조회"""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_kakao_id(self, kakao_id: str) -> Optional[User]:
        """카카오 ID로 사용자 조회"""
        stmt = select(User).where(User.kakao_id == kakao_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: Optional[str],
        name: str,
        phone: Optional[str] = None,
        kakao_id: Optional[str] = None,
        role: str = "owner",
        plan: str = "free"
    ) -> User:
        """사용자 생성"""
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name,
            phone=phone,
            kakao_id=kakao_id,
            role=role,
            plan=plan,
            is_active=True
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(
        self,
        user: User,
        name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> User:
        """사용자 정보 수정"""
        if name is not None:
            user.name = name
        if phone is not None:
            user.phone = phone

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        """비밀번호 수정"""
        user.hashed_password = hashed_password
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def deactivate(self, user: User) -> User:
        """사용자 비활성화"""
        user.is_active = False
        await self.db.flush()
        return user
