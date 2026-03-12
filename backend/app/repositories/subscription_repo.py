# Subscription Repository
from typing import Optional, List
from datetime import datetime, date, timezone
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.subscription import Subscription
from app.core.exceptions import SubscriptionActiveError


class SubscriptionRepository:
    """Subscription Repository"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id,
        plan: str,
        starts_at: datetime,
        expires_at: datetime,
        monthly_amount: int,
        toss_customer_key: Optional[str] = None,
        toss_billing_key: Optional[str] = None,
        toss_order_id: Optional[str] = None
    ) -> Subscription:
        """구독 생성"""
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status="active",
            starts_at=starts_at,
            expires_at=expires_at,
            monthly_amount=monthly_amount,
            toss_customer_key=toss_customer_key,
            toss_billing_key=toss_billing_key,
            toss_order_id=toss_order_id
        )

        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def get_active_by_user(self, user_id) -> Optional[Subscription]:
        """사용자의 활성 구독 조회"""
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, subscription_id) -> Optional[Subscription]:
        """구독 ID로 조회"""
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        subscription: Subscription,
        **kwargs
    ) -> Subscription:
        """구독 업데이트"""
        for key, value in kwargs.items():
            setattr(subscription, key, value)

        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def cancel(
        self,
        subscription: Subscription,
        cancelled_at: datetime
    ) -> Subscription:
        """구독 취소"""
        subscription.status = "cancelled"
        subscription.cancelled_at = cancelled_at
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def expire_old_subscriptions(self) -> int:
        """만료된 구독 처리"""
        now = datetime.now(timezone.utc)

        # 만료 처리
        result = await self.db.execute(
            select(func.count()).where(
                Subscription.status == "active",
                Subscription.expires_at < now
            )
        )
        count = result.scalar()

        # 상태 업데이트
        if count > 0:
            await self.db.execute(
                Subscription.__table__.update()
                .where(
                    Subscription.status == "active",
                    Subscription.expires_at < now
                )
                .values(status="expired")
            )
            await self.db.commit()

        return count

    async def get_by_toss_order_id(self, order_id: str) -> Optional[Subscription]:
        """토스 주문 ID로 구독 조회"""
        result = await self.db.execute(
            select(Subscription).where(Subscription.toss_order_id == order_id)
        )
        return result.scalar_one_or_none()
