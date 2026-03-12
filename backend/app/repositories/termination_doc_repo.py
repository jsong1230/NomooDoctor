# 해고 서류 저장소
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.severance import TerminationDocument


class TerminationDocRepository:
    """TerminationDocument 저장소"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> TerminationDocument:
        """해고 서류 생성"""
        doc = TerminationDocument(**data)
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get_by_id_and_company(self, id: UUID, company_id: UUID) -> TerminationDocument | None:
        """ID와 회사로 해고 서류 조회"""
        result = await self.db.execute(
            select(TerminationDocument).where(
                and_(
                    TerminationDocument.id == id,
                    TerminationDocument.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_employee(self, employee_id: UUID) -> list[TerminationDocument]:
        """직원별 해고 서류 목록 조회"""
        result = await self.db.execute(
            select(TerminationDocument).where(
                TerminationDocument.employee_id == employee_id
            ).order_by(TerminationDocument.created_at.desc())
        )
        return result.scalars().all()
