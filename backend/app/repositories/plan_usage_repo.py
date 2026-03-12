# Plan Usage Repository
from typing import Optional, Dict, Any
from datetime import datetime, date, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.subscription import PlanUsage


class PlanUsageRepository:
    """Plan Usage Repository"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(
        self,
        user_id,
        month: date
    ) -> PlanUsage:
        """사용량 레코드 조회 또는 생성"""
        # 해당 월의 사용량 조회
        first_day = date(month.year, month.month, 1)

        result = await self.db.execute(
            select(PlanUsage).where(
                PlanUsage.user_id == user_id,
                PlanUsage.usage_month == first_day
            )
        )
        usage = result.scalar_one_or_none()

        if not usage:
            usage = PlanUsage(
                user_id=user_id,
                usage_month=first_day,
                chat_count=0,
                contract_count=0,
                payslip_send_count=0,
                attorney_consult_count=0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(usage)
            await self.db.commit()
            await self.db.refresh(usage)

        return usage

    async def increment(
        self,
        usage: PlanUsage,
        usage_type: str
    ) -> PlanUsage:
        """사용량 증가"""
        if usage_type == "chat":
            usage.chat_count += 1
        elif usage_type == "contract":
            usage.contract_count += 1
        elif usage_type == "payslip_send":
            usage.payslip_send_count += 1
        elif usage_type == "attorney_consult":
            usage.attorney_consult_count += 1

        usage.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(usage)
        return usage

    async def get_current_usage(self, user_id) -> Dict[str, int]:
        """현재 월 사용량 조회"""
        today = date.today()
        first_day = date(today.year, today.month, 1)

        result = await self.db.execute(
            select(PlanUsage).where(
                PlanUsage.user_id == user_id,
                PlanUsage.usage_month == first_day
            )
        )
        usage = result.scalar_one_or_none()

        if not usage:
            return {
                "chat_count": 0,
                "contract_count": 0,
                "payslip_send_count": 0,
                "attorney_consult_count": 0
            }

        return {
            "chat_count": usage.chat_count,
            "contract_count": usage.contract_count,
            "payslip_send_count": usage.payslip_send_count,
            "attorney_consult_count": usage.attorney_consult_count
        }

    async def update_monthly_usage(
        self,
        user_id,
        month: date,
        chat_count: int,
        contract_count: int,
        payslip_send_count: int,
        attorney_consult_count: int
    ) -> PlanUsage:
        """월별 사용량 업데이트"""
        first_day = date(month.year, month.month, 1)

        result = await self.db.execute(
            select(PlanUsage).where(
                PlanUsage.user_id == user_id,
                PlanUsage.usage_month == first_day
            )
        )
        usage = result.scalar_one_or_none()

        if not usage:
            usage = PlanUsage(
                user_id=user_id,
                usage_month=first_day,
                chat_count=chat_count,
                contract_count=contract_count,
                payslip_send_count=payslip_send_count,
                attorney_consult_count=attorney_consult_count,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(usage)
        else:
            usage.chat_count = chat_count
            usage.contract_count = contract_count
            usage.payslip_send_count = payslip_send_count
            usage.attorney_consult_count = attorney_consult_count
            usage.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(usage)
        return usage
