# Contract Repository
from typing import Optional, List
from datetime import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models.contract import Contract


class ContractRepository:
    """Contract CRUD 작업을 담당하는 Repository"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, contract_id: uuid.UUID | str) -> Optional[Contract]:
        """ID로 계약서 조회"""
        if isinstance(contract_id, str):
            contract_id = uuid.UUID(contract_id)

        stmt = select(Contract).where(Contract.id == contract_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_company(
        self,
        contract_id: uuid.UUID | str,
        company_id: uuid.UUID | str
    ) -> Optional[Contract]:
        """회사 ID와 계약서 ID로 조회"""
        from sqlalchemy.orm import selectinload

        if isinstance(contract_id, str):
            contract_id = uuid.UUID(contract_id)
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = (
            select(Contract)
            .options(selectinload(Contract.employee))
            .where(
                Contract.id == contract_id,
                Contract.company_id == company_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: uuid.UUID | str,
        employee_id: Optional[uuid.UUID | str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Contract]:
        """회사별 계약서 목록 조회"""
        from sqlalchemy.orm import selectinload

        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)
        if employee_id and isinstance(employee_id, str):
            employee_id = uuid.UUID(employee_id)

        stmt = (
            select(Contract)
            .options(selectinload(Contract.employee))
            .where(Contract.company_id == company_id)
        )

        if employee_id is not None:
            stmt = stmt.where(Contract.employee_id == employee_id)

        if status is not None:
            stmt = stmt.where(Contract.status == status)

        stmt = stmt.order_by(Contract.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_company(
        self,
        company_id: uuid.UUID | str,
        employee_id: Optional[uuid.UUID | str] = None,
        status: Optional[str] = None
    ) -> int:
        """회사별 계약서 수 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)
        if employee_id and isinstance(employee_id, str):
            employee_id = uuid.UUID(employee_id)

        from sqlalchemy import func
        stmt = select(func.count(Contract.id)).where(Contract.company_id == company_id)

        if employee_id is not None:
            stmt = stmt.where(Contract.employee_id == employee_id)

        if status is not None:
            stmt = stmt.where(Contract.status == status)

        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_by_sign_ref(self, sign_service_ref: str) -> Optional[Contract]:
        """모두싸인 문서 ID로 계약서 조회"""
        stmt = select(Contract).where(Contract.sign_service_ref == sign_service_ref)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        company_id: uuid.UUID,
        employee_id: uuid.UUID,
        contract_type: str,
        start_date,
        work_location: str,
        work_hours_per_week: float,
        work_start_time: str,
        work_end_time: str,
        break_minutes: int = 60,
        work_days: str = "월화수목금",
        wage_type: str = "monthly",
        base_wage: float = 0,
        meal_allowance: float = 0,
        transport_allowance: float = 0,
        probation_months: int = 0,
        probation_wage_rate: float = 1.0,
        nda_included: bool = False,
        non_compete_included: bool = False,
        end_date=None,
        status: str = "draft",
        ai_generated: bool = True,
        ai_model: str = None
    ) -> Contract:
        """계약서 생성"""
        # 시간 문자열을 time 객체로 변환
        start_hour, start_minute = map(int, work_start_time.split(":"))
        end_hour, end_minute = map(int, work_end_time.split(":"))

        contract = Contract(
            company_id=company_id,
            employee_id=employee_id,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            work_location=work_location,
            work_hours_per_week=work_hours_per_week,
            work_start_time=time(hour=start_hour, minute=start_minute),
            work_end_time=time(hour=end_hour, minute=end_minute),
            break_minutes=break_minutes,
            work_days=work_days,
            wage_type=wage_type,
            base_wage=base_wage,
            meal_allowance=meal_allowance,
            transport_allowance=transport_allowance,
            probation_months=probation_months,
            probation_wage_rate=probation_wage_rate,
            nda_included=nda_included,
            non_compete_included=non_compete_included,
            status=status,
            ai_generated=ai_generated,
            ai_model=ai_model
        )
        self.db.add(contract)
        await self.db.flush()
        await self.db.refresh(contract)
        return contract
