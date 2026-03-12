# Chat Repository
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models.chat import ChatSession, ChatMessage


class ChatRepository:
    """채팅 세션 및 메시지 CRUD"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(
        self,
        user_id: uuid.UUID,
        company_id: uuid.UUID | None = None,
        title: str | None = None,
    ) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            company_id=company_id,
            title=title,
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[ChatSession]:
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sessions(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> list[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        session = await self.get_session(session_id, user_id)
        if session is None:
            return False
        await self.db.delete(session)
        await self.db.flush()
        return True

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        law_references: dict | None = None,
        risk_level: str | None = None,
        disclaimer_shown: bool = False,
        tokens_used: int | None = None,
        model_used: str | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            law_references=law_references,
            risk_level=risk_level,
            disclaimer_shown=disclaimer_shown,
            tokens_used=tokens_used,
            model_used=model_used,
        )
        self.db.add(message)

        # 세션 메시지 카운트 + 위험도 에스컬레이션
        session_stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await self.db.execute(session_stmt)
        session = result.scalar_one_or_none()
        if session:
            session.message_count += 1
            if risk_level:
                risk_order = {"low": 0, "medium": 1, "high": 2, "emergency": 3}
                current = risk_order.get(session.risk_level, 0)
                new = risk_order.get(risk_level, 0)
                if new > current:
                    session.risk_level = risk_level

        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_messages(
        self, session_id: uuid.UUID, limit: int = 40
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_session_attorney_referred(
        self, session_id: uuid.UUID
    ) -> None:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            session.attorney_referred = True
            await self.db.flush()
