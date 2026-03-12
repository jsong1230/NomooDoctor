# 퇴직금 기록 저장소
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.db.models.severance import SeveranceRecord


class SeveranceRepository:
    """SeveranceRecord 저장소"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> SeveranceRecord:
        """퇴직금 기록 생성"""
        record = SeveranceRecord(**data)
        self.db.add(record)
        await self.db.flush()
        return record

    async def get_by_id(self, id: UUID) -> SeveranceRecord | None:
        """ID로 퇴직금 기록 조회"""
        result = await self.db.execute(
            select(SeveranceRecord).where(SeveranceRecord.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_company(self, id: UUID, company_id: UUID) -> SeveranceRecord | None:
        """ID와 회사로 퇴직금 기록 조회"""
        result = await self.db.execute(
            select(SeveranceRecord).where(
                and_(
                    SeveranceRecord.id == id,
                    SeveranceRecord.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_employee_and_date(
        self, employee_id: UUID, resign_date: date
    ) -> SeveranceRecord | None:
        """직원과 퇴사일로 퇴직금 기록 조회"""
        result = await self.db.execute(
            select(SeveranceRecord).where(
                and_(
                    SeveranceRecord.employee_id == employee_id,
                    SeveranceRecord.resign_date == resign_date
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: UUID,
        employee_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[SeveranceRecord]:
        """회사별 퇴직금 기록 목록 조회"""
        query = select(SeveranceRecord).where(SeveranceRecord.company_id == company_id)

        if employee_id:
            query = query.where(SeveranceRecord.employee_id == employee_id)

        if status:
            query = query.where(SeveranceRecord.status == status)

        query = query.order_by(SeveranceRecord.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_status(
        self, id: UUID, status: str, paid_at: date | None = None
    ) -> SeveranceRecord | None:
        """퇴직금 기록 상태 업데이트"""
        record = await self.get_by_id(id)
        if not record:
            return None

        record.status = status
        if paid_at:
            record.paid_at = paid_at
        record.updated_at = date.today()
        await self.db.flush()
        return record
