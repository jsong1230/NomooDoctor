# 근무 기록 레포지토리
from datetime import date
from uuid import UUID
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.db.models.salary import WorkRecord
from app.db.models.employee import Employee


class WorkRecordRepository:
    """근무 기록 데이터 접근 계층"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, record_id: UUID) -> WorkRecord | None:
        """ID로 근무 기록 조회"""
        stmt = select(WorkRecord).where(WorkRecord.id == record_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_company(self, record_id: UUID, company_id: UUID) -> WorkRecord | None:
        """ID와 company_id로 근무 기록 조회 (권한 확인용)"""
        stmt = select(WorkRecord).where(
            and_(WorkRecord.id == record_id, WorkRecord.company_id == company_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_and_date(self, employee_id: UUID, work_date: date) -> WorkRecord | None:
        """직원과 날짜로 근무 기록 조회"""
        stmt = select(WorkRecord).where(
            and_(WorkRecord.employee_id == employee_id, WorkRecord.work_date == work_date)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: UUID,
        employee_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 50,
        cursor: str | None = None
    ) -> tuple[list[WorkRecord], str | None]:
        """사업장별 근무 기록 목록 조회 (커서 기반 페이지네이션)"""
        conditions = [WorkRecord.company_id == company_id]

        if employee_id:
            conditions.append(WorkRecord.employee_id == employee_id)

        if from_date:
            conditions.append(WorkRecord.work_date >= from_date)

        if to_date:
            conditions.append(WorkRecord.work_date <= to_date)

        stmt = select(WorkRecord).where(and_(*conditions))
        stmt = stmt.order_by(desc(WorkRecord.work_date), desc(WorkRecord.id))
        stmt = stmt.limit(limit + 1)  # 다음 페이지 여부 확인용

        result = await self.db.execute(stmt)
        records = result.scalars().all()

        # 커서 계산
        has_next = len(records) > limit
        records = records[:limit]
        next_cursor = None
        if has_next and records:
            last_record = records[-1]
            next_cursor = f"{last_record.work_date.isoformat()}:{last_record.id}"

        return records, next_cursor

    async def create(self, **kwargs) -> WorkRecord:
        """근무 기록 생성"""
        record = WorkRecord(**kwargs)
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_batch(self, records: list[dict]) -> list[WorkRecord]:
        """근무 기록 일괄 생성"""
        work_records = [WorkRecord(**data) for data in records]
        self.db.add_all(work_records)
        await self.db.flush()
        return work_records

    async def update(self, record: WorkRecord, **kwargs) -> WorkRecord:
        """근무 기록 수정"""
        for key, value in kwargs.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)
        await self.db.flush()
        return record

    async def delete(self, record: WorkRecord) -> None:
        """근무 기록 삭제"""
        await self.db.delete(record)
        await self.db.flush()

    async def get_monthly_aggregation(
        self,
        company_id: UUID,
        year: int,
        month: int,
        employee_id: UUID | None = None
    ) -> list[dict]:
        """월별 집계 조회"""
        from sqlalchemy import extract

        conditions = [
            WorkRecord.company_id == company_id,
            extract('year', WorkRecord.work_date) == year,
            extract('month', WorkRecord.work_date) == month,
        ]

        if employee_id:
            conditions.append(WorkRecord.employee_id == employee_id)

        stmt = select(
            WorkRecord.employee_id,
            func.count(WorkRecord.id).label('work_days'),
            func.sum(
                func.cast(WorkRecord.scheduled_end, func.cast(WorkRecord.scheduled_start, int)) -
                func.cast(WorkRecord.scheduled_start, int)
            ).label('scheduled_minutes'),
            func.sum(WorkRecord.break_minutes).label('total_break_minutes'),
            func.sum(WorkRecord.overtime_minutes).label('total_overtime_minutes'),
            func.sum(WorkRecord.night_minutes).label('total_night_minutes'),
            func.sum(WorkRecord.holiday_minutes).label('total_holiday_minutes'),
        ).where(and_(*conditions)).group_by(WorkRecord.employee_id)

        # 직접 SQL로 처리하는 것이 더 정확함
        # 여기서는 간단한 집계만 진행하고 복잡한 계산은 서비스에서 수행

        from sqlalchemy.sql import text

        query = f"""
        SELECT
            employee_id,
            COUNT(DISTINCT work_date) as work_days,
            SUM(break_minutes) as total_break_minutes,
            SUM(overtime_minutes) as total_overtime_minutes,
            SUM(night_minutes) as total_night_minutes,
            SUM(holiday_minutes) as total_holiday_minutes,
            SUM(EXTRACT(EPOCH FROM (actual_end::time - actual_start::time - break_minutes * INTERVAL '1 minute')) / 60)::int as total_work_minutes
        FROM work_records
        WHERE company_id = :company_id
            AND EXTRACT(YEAR FROM work_date) = :year
            AND EXTRACT(MONTH FROM work_date) = :month
            {f'AND employee_id = :employee_id' if employee_id else ''}
        GROUP BY employee_id
        """

        params = {'company_id': str(company_id), 'year': year, 'month': month}
        if employee_id:
            params['employee_id'] = str(employee_id)

        result = await self.db.execute(text(query), params)
        rows = result.fetchall()

        return [dict(row._mapping) for row in rows]

    async def get_employee_stats(
        self,
        employee_id: UUID,
        from_date: date,
        to_date: date
    ) -> dict:
        """직원 근무 패턴 분석 통계"""
        conditions = [
            WorkRecord.employee_id == employee_id,
            WorkRecord.work_date >= from_date,
            WorkRecord.work_date <= to_date,
            WorkRecord.actual_start.is_not(None),
            WorkRecord.actual_end.is_not(None),
        ]

        stmt = select(WorkRecord).where(and_(*conditions))
        result = await self.db.execute(stmt)
        records = result.scalars().all()

        return {
            "records": records,
            "count": len(records),
        }

    async def count_late_early_absent(
        self,
        employee_id: UUID,
        year: int,
        month: int
    ) -> dict:
        """지각/조퇴/결근 카운트"""
        from sqlalchemy import extract, case

        conditions = [
            WorkRecord.employee_id == employee_id,
            extract('year', WorkRecord.work_date) == year,
            extract('month', WorkRecord.work_date) == month,
        ]

        stmt = select(
            func.sum(case((WorkRecord.actual_start > WorkRecord.scheduled_start, 1), else_=0)).label('late'),
            func.sum(case((WorkRecord.actual_end < WorkRecord.scheduled_end, 1), else_=0)).label('early_leave'),
        ).where(and_(*conditions))

        result = await self.db.execute(stmt)
        row = result.one()

        return {
            "late": row.late or 0,
            "early_leave": row.early_leave or 0,
            "absent": 0,  # 별도 로직으로 계산 필요
        }
