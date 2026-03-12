# Payment Service
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.subscription import Subscription, PaymentHistory
from app.repositories.payment_repo import PaymentRepository
from app.repositories.plan_usage_repo import PlanUsageRepository
from app.schemas.subscription import BillingKeyResponse
from app.core.exceptions import (
    BillingKeyAlreadyExistsError,
    BillingKeyRegisterError,
    PaymentFailedError
)
from app.external.toss_client import TossClient


class PaymentService:
    """결제 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.plan_usage_repo = PlanUsageRepository(db)

    async def register_billing_key(
        self,
        user: User,
        auth_key: str,
        customer_key: str
    ) -> BillingKeyResponse:
        """빌링키 등록"""
        # 이미 등록된 빌링키 확인
        existing_billing_key = await self.payment_repo.get_billing_key_by_user(user.id)
        if existing_billing_key:
            raise BillingKeyAlreadyExistsError()

        # Toss API 호출
        async with TossClient() as toss_client:
            result = await toss_client.issue_billing_key(
                auth_key=auth_key,
                customer_key=customer_key
            )

            return BillingKeyResponse(
                billing_key=result["billingKey"],
                card_company=result["cardCompany"],
                card_number=result["cardNumber"],
                card_type=result["cardType"],
                registered_at=datetime.now(timezone.utc)
            )

    async def charge_with_billing_key(
        self,
        billing_key: str,
        amount: int,
        order_id: str,
        customer_key: str
    ) -> Dict[str, Any]:
        """빌링키로 결제"""
        async with TossClient() as toss_client:
            result = await toss_client.charge(
                billing_key=billing_key,
                amount=amount,
                order_id=order_id,
                customer_key=customer_key
            )

            return result

    async def process_webhook(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """웹훅 처리"""
        from app.repositories.subscription_repo import SubscriptionRepository

        subscription_repo = SubscriptionRepository(self.db)

        if event_type == "PAYMENT_STATUS_CHANGED":
            payment_id = data.get("paymentId")
            order_id = data.get("orderId")
            status = data.get("status")

            if not payment_id or not order_id:
                return

            # 이미 처리된 웹훅인지 확인
            existing = await self.payment_repo.get_by_toss_payment_id(payment_id)
            if existing:
                return

            # 구독 조회
            subscription = await subscription_repo.get_by_toss_order_id(order_id)
            if not subscription:
                return

            # 결제 이력 생성
            payment = PaymentHistory(
                subscription_id=subscription.id,
                user_id=subscription.user_id,
                toss_payment_id=payment_id,
                toss_order_id=order_id,
                amount=subscription.monthly_amount,
                status=status.lower(),
                created_at=datetime.now(timezone.utc)
            )

            self.db.add(payment)

            if status == "DONE":
                # 결제 성공: 구독 연장
                from datetime import timedelta as td
                subscription.expires_at = datetime.now(timezone.utc) + td(days=30)
                payment.paid_at = datetime.now(timezone.utc)
            elif status == "FAILED":
                # 결제 실패: 재시도 설정
                payment.failed_at = datetime.now(timezone.utc)
                payment.failure_reason = data.get("failure", {}).get("message", "")
                await self.handle_failed_payment(subscription, payment.failure_reason)

            await self.db.commit()

        elif event_type == "BILLING_KEY_STATUS_CHANGED":
            # 빌링키 상태 변경 처리
            # 사용자에게 알림 발송 등의 로직 구현 필요
            pass

    async def get_payment_history(
        self,
        user: User,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """결제 내역 조회"""
        result = await self.payment_repo.get_paginated_by_user(
            user_id=str(user.id),
            limit=limit,
            cursor=cursor
        )

        # Pydantic 모델 변환
        from app.schemas.subscription import PaymentHistoryItem, PaginationMeta

        payments = [
            PaymentHistoryItem(
                id=p.id,
                toss_payment_id=p.toss_payment_id,
                amount=p.amount,
                status=p.status,
                payment_method=p.payment_method,
                paid_at=p.paid_at
            )
            for p in result["payments"]
        ]

        return {
            "payments": payments,
            "pagination": PaginationMeta(
                cursor=result["cursor"],
                has_next=result["has_next"],
                limit=result["limit"],
                total_count=result["total_count"]
            )
        }

    async def handle_failed_payment(
        self,
        subscription: Subscription,
        error: str
    ) -> None:
        """결제 실패 처리"""
        # 재시도 횟수 증가
        from sqlalchemy import update

        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription.id)
            .values(
                status="paused",
                cancelled_at=datetime.now(timezone.utc)
            )
        )
        await self.db.commit()

        # 재시도 스케줄링 (Mock 모드에서는 생략)
        # 실제 환경에서는 Celery 등을 사용하여 재시도 큐에 추가
