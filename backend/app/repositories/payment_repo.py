# Payment History Repository
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.subscription import PaymentHistory


class PaymentRepository:
    """Payment History Repository"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        subscription_id,
        user_id,
        toss_payment_id: Optional[str],
        toss_order_id: str,
        amount: int,
        status: str,
        payment_method: Optional[str] = None,
        paid_at: Optional[datetime] = None,
        failed_at: Optional[datetime] = None,
        failure_reason: Optional[str] = None,
        refund_amount: Optional[int] = None,
        refunded_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentHistory:
        """결제 이력 생성"""
        payment = PaymentHistory(
            subscription_id=subscription_id,
            user_id=user_id,
            toss_payment_id=toss_payment_id,
            toss_order_id=toss_order_id,
            amount=amount,
            status=status,
            payment_method=payment_method,
            paid_at=paid_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            refund_amount=refund_amount,
            refunded_at=refunded_at,
            metadata=metadata,
            created_at=datetime.now(timezone.utc)
        )

        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_by_id(self, payment_id: str) -> Optional[PaymentHistory]:
        """결제 이력 ID로 조회"""
        result = await self.db.execute(
            select(PaymentHistory).where(PaymentHistory.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_toss_payment_id(self, toss_payment_id: str) -> Optional[PaymentHistory]:
        """토스 결제 ID로 조회"""
        result = await self.db.execute(
            select(PaymentHistory).where(PaymentHistory.toss_payment_id == toss_payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_toss_order_id(self, toss_order_id: str) -> Optional[PaymentHistory]:
        """토스 주문 ID로 조회"""
        result = await self.db.execute(
            select(PaymentHistory).where(PaymentHistory.toss_order_id == toss_order_id)
        )
        return result.scalar_one_or_none()

    async def get_paginated_by_user(
        self,
        user_id: str,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """사용자의 결제 내역 페이징 조회"""
        # 최신순 정렬
        stmt = (
            select(PaymentHistory)
            .where(PaymentHistory.user_id == user_id)
            .order_by(PaymentHistory.created_at.desc())
        )

        # 커서 기반 페이지네이션
        if cursor:
            # cursor가 마지막 ID라고 가정
            stmt = stmt.where(PaymentHistory.id < cursor)

        stmt = stmt.limit(limit + 1)

        result = await self.db.execute(stmt)
        payments = result.scalars().all()

        has_next = len(payments) > limit
        if has_next:
            payments = payments[:limit]
            next_cursor = str(payments[-1].id)
        else:
            next_cursor = None

        return {
            "payments": payments,
            "cursor": next_cursor,
            "has_next": has_next,
            "limit": limit,
            "total_count": await self._count_by_user(user_id)
        }

    async def _count_by_user(self, user_id: str) -> int:
        """사용자 결제 이력 수"""
        result = await self.db.execute(
            select(func.count()).where(PaymentHistory.user_id == user_id)
        )
        return result.scalar()

    async def get_billing_key_by_user(self, user_id: str) -> Optional[PaymentHistory]:
        """사용자의 활성 빌링키 조회"""
        # subscription에서 직접 조회 (payment_history에도 있지만)
        from app.db.models.subscription import Subscription
        from app.db.models.user import User

        result = await self.db.execute(
            select(Subscription.toss_billing_key)
            .join(User, Subscription.user_id == User.id)
            .where(
                User.id == user_id,
                Subscription.toss_billing_key.isnot(None)
            )
        )
        return result.scalar()
