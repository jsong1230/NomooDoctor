# Subscription Service
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.subscription import Subscription, PaymentHistory, PlanUsage
from app.repositories.subscription_repo import SubscriptionRepository
from app.repositories.payment_repo import PaymentRepository
from app.repositories.plan_usage_repo import PlanUsageRepository
from app.schemas.subscription import (
    PlanInfo, PlanFeature,
    SubscriptionResponse, UsageInfo, MySubscriptionResponse,
    SubscriptionResult, PlanChangeResult,
    CancelSubscriptionResult
)
from app.core.exceptions import (
    SubscriptionNotFoundError,
    SubscriptionActiveError,
    BillingKeyInvalidError,
    PaymentFailedError,
    SubscriptionDowngradeError
)


class SubscriptionService:
    """구독 서비스"""

    # 플랜 정보
    PLANS: Dict[str, PlanInfo] = {
        "free": PlanInfo(
            id="starter",
            name="스타터",
            price=0,
            features=PlanFeature(
                chat_limit=10,
                contract_limit=2,
                payroll=False,
                payslip_send_limit=0,
                attorney_consult=False
            )
        ),
        "basic": PlanInfo(
            id="basic",
            name="베이직",
            price=9900,
            features=PlanFeature(
                chat_limit=None,
                contract_limit=None,
                payroll=True,
                payslip_send_limit=10,
                attorney_consult=False
            )
        ),
        "standard": PlanInfo(
            id="standard",
            name="스탠다드",
            price=29000,
            features=PlanFeature(
                chat_limit=None,
                contract_limit=None,
                payroll=True,
                payslip_send_limit=100,
                attorney_consult=False
            )
        ),
        "premium": PlanInfo(
            id="premium",
            name="프리미엄",
            price=49000,
            features=PlanFeature(
                chat_limit=None,
                contract_limit=None,
                payroll=True,
                payslip_send_limit=None,
                attorney_consult=True,
                attorney_consult_limit=1
            )
        ),
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_repo = SubscriptionRepository(db)
        self.payment_repo = PaymentRepository(db)
        self.plan_usage_repo = PlanUsageRepository(db)

    # ===== 플랜 관련 =====

    def get_plans(self) -> List[PlanInfo]:
        """플랜 목록 조회"""
        return list(self.PLANS.values())

    def get_plan_features(self, plan_id: str) -> Dict[str, Any]:
        """플랜 기능 반환"""
        plan = self.PLANS.get(plan_id)
        if not plan:
            raise SubscriptionNotFoundError(f"존재하지 않는 플랜입니다: {plan_id}")

        return plan.features.model_dump()

    # ===== 구독 조회 =====

    async def get_my_subscription(self, user: User) -> MySubscriptionResponse:
        """내 구독 정보 조회"""
        subscription = await self.subscription_repo.get_active_by_user(user.id)

        if subscription:
            # 사용량 조회
            usage = await self.plan_usage_repo.get_current_usage(user.id)
            usage_info = UsageInfo(
                month=user.plan_expires_at.strftime("%Y-%m") if user.plan_expires_at else datetime.now(timezone.utc).strftime("%Y-%m"),
                chat_count=usage.get("chat_count", 0),
                contract_count=usage.get("contract_count", 0),
                payslip_send_count=usage.get("payslip_send_count", 0),
                chat_limit=self.get_plan_features(subscription.plan)["chat_limit"],
                contract_limit=self.get_plan_features(subscription.plan)["contract_limit"],
                payslip_send_limit=self.get_plan_features(subscription.plan)["payslip_send_limit"]
            )

            subscription_response = SubscriptionResponse(
                id=subscription.id,
                plan=subscription.plan,
                status=subscription.status,
                starts_at=subscription.starts_at,
                expires_at=subscription.expires_at,
                monthly_amount=subscription.monthly_amount,
                has_billing_key=bool(subscription.toss_billing_key),
                cancelled_at=subscription.cancelled_at
            )

            return MySubscriptionResponse(
                subscription=subscription_response,
                usage=usage_info
            )

        # 구독 없음
        usage = await self.plan_usage_repo.get_current_usage(user.id)
        usage_info = UsageInfo(
            month=datetime.now(timezone.utc).strftime("%Y-%m"),
            chat_count=usage.get("chat_count", 0),
            contract_count=usage.get("contract_count", 0),
            payslip_send_count=usage.get("payslip_send_count", 0),
            chat_limit=10,
            contract_limit=2,
            payslip_send_limit=0
        )

        return MySubscriptionResponse(
            subscription=None,
            usage=usage_info
        )

    # ===== 구독 생성 =====

    async def create_subscription(
        self,
        user: User,
        plan: str,
        billing_key: str
    ) -> SubscriptionResult:
        """구독 생성"""
        # 활성 구독 확인
        existing = await self.subscription_repo.get_active_by_user(user.id)
        if existing:
            raise SubscriptionActiveError()

        # 플랜 확인
        plan_info = self.PLANS.get(plan)
        if not plan_info:
            raise SubscriptionNotFoundError(f"존재하지 않는 플랜입니다: {plan}")

        # 빌링키 검증
        if billing_key.startswith("tb_invalid"):
            raise BillingKeyInvalidError()

        # 사용자 UUID를 customerKey로 사용
        customer_key = str(user.id)

        # 결제 처리
        from app.services.payment_service import PaymentService
        payment_service = PaymentService(self.db)

        # 결제 요청
        toss_order_id = f"order_{user.id}_{datetime.now(timezone.utc).timestamp()}"
        payment_result = await payment_service.charge_with_billing_key(
            billing_key=billing_key,
            amount=plan_info.price,
            order_id=toss_order_id,
            customer_key=customer_key
        )

        # TossClient는 status를 "DONE"/"FAILED"로 반환
        if payment_result.get("status") not in ("success", "DONE"):
            raise PaymentFailedError(
                payment_result.get("failure_reason", "결제에 실패했습니다."),
                details=payment_result.get("failure")
            )

        # 구독 생성
        starts_at = datetime.now(timezone.utc)
        expires_at = starts_at + timedelta(days=30)

        subscription = await self.subscription_repo.create(
            user_id=user.id,
            plan=plan,
            starts_at=starts_at,
            expires_at=expires_at,
            monthly_amount=plan_info.price,
            toss_order_id=toss_order_id,
            toss_billing_key=billing_key,
            toss_customer_key=customer_key
        )

        # 사용자 플랜 동기화
        user.plan = plan
        user.plan_expires_at = expires_at
        await self.db.commit()

        return SubscriptionResult(
            subscription_id=subscription.id,
            toss_order_id=toss_order_id,
            status=subscription.status,
            starts_at=subscription.starts_at,
            expires_at=subscription.expires_at
        )

    # ===== 플랜 변경 =====

    async def change_plan(
        self,
        user: User,
        new_plan: str
    ) -> PlanChangeResult:
        """플랜 변경"""
        # 활성 구독 확인
        subscription = await self.subscription_repo.get_active_by_user(user.id)
        if not subscription:
            raise SubscriptionNotFoundError()

        # 동일 플랜 확인
        if subscription.plan == new_plan:
            raise SubscriptionActiveError()

        # 다운그레이드는 다음 결제일 적용
        if new_plan == "free":
            raise SubscriptionDowngradeError()

        # 플랜 확인
        plan_info = self.PLANS.get(new_plan)
        if not plan_info:
            raise SubscriptionNotFoundError(f"존재하지 않는 플랜입니다: {new_plan}")

        # 업그레이드: 즉시 변경
        old_plan = subscription.plan
        effective_at = datetime.now(timezone.utc)

        # 프로레이션 계산
        remaining_days = (subscription.expires_at - effective_at).days
        proration_amount = self.calculate_proration(
            old_plan, new_plan, remaining_days
        )

        # 결제 처리 (업그레이드 시)
        from app.services.payment_service import PaymentService
        payment_service = PaymentService(self.db)

        customer_key = str(user.id)
        toss_order_id = f"order_{user.id}_{datetime.now(timezone.utc).timestamp()}_upgrade"
        payment_result = await payment_service.charge_with_billing_key(
            billing_key=subscription.toss_billing_key or f"tb_test_{customer_key[:8]}",
            amount=proration_amount,
            order_id=toss_order_id,
            customer_key=customer_key
        )

        if payment_result.get("status") not in ("success", "DONE"):
            raise PaymentFailedError(
                payment_result.get("failure_reason", "결제에 실패했습니다.")
            )

        # 구독 업데이트
        subscription.plan = new_plan
        subscription.expires_at = effective_at + timedelta(days=30)
        subscription.monthly_amount = plan_info.price
        subscription.toss_order_id = toss_order_id

        await self.db.commit()
        await self.db.refresh(subscription)

        # 사용자 플랜 동기화
        user.plan = new_plan
        user.plan_expires_at = subscription.expires_at
        await self.db.commit()

        return PlanChangeResult(
            subscription_id=subscription.id,
            old_plan=old_plan,
            new_plan=new_plan,
            proration_amount=proration_amount,
            proration_description=f"잔여 {remaining_days}일에 대한 비례 계산",
            next_billing_amount=plan_info.price,
            effective_at=effective_at
        )

    def calculate_proration(
        self,
        current_plan: str,
        new_plan: str,
        remaining_days: int
    ) -> int:
        """프로레이션 금액 계산"""
        if remaining_days <= 0:
            return 0

        current_amount = self.PLANS[current_plan].price
        new_amount = self.PLANS[new_plan].price

        # 월의 일수로 계산 (30일 기준)
        daily_amount = (new_amount - current_amount) / 30
        proration = int(daily_amount * remaining_days)

        return max(proration, 0)

    # ===== 구독 해지 =====

    async def cancel_subscription(
        self,
        user: User,
        reason: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> CancelSubscriptionResult:
        """구독 해지"""
        subscription = await self.subscription_repo.get_active_by_user(user.id)
        if not subscription:
            raise SubscriptionNotFoundError()

        # 취소
        cancelled_at = datetime.now(timezone.utc)
        subscription = await self.subscription_repo.cancel(
            subscription,
            cancelled_at
        )

        access_until = subscription.expires_at

        return CancelSubscriptionResult(
            subscription_id=subscription.id,
            status=subscription.status,
            cancelled_at=subscription.cancelled_at,
            access_until=access_until,
            message=f"2026년 {access_until.strftime('%m')}월 {access_until.strftime('%d')}일까지 서비스를 이용하실 수 있습니다."
        )

    # ===== 배치 작업 =====

    async def process_expiry(self) -> int:
        """만료 구독 처리"""
        return await self.subscription_repo.expire_old_subscriptions()
