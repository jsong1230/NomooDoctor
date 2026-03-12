"""
F-11 구독 및 결제 — 서비스 단위 테스트
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock


from app.services.subscription_service import SubscriptionService
from app.services.plan_service import PlanService
from app.core.exceptions import (
    SubscriptionNotFoundError,
    SubscriptionActiveError,
    BillingKeyInvalidError,
)


class MockDB:
    pass


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.name = "테스트사용자"
    user.plan = "free"
    user.plan_expires_at = None
    return user


@pytest.fixture
def mock_subscription():
    sub = MagicMock()
    sub.id = uuid.uuid4()
    sub.user_id = uuid.uuid4()
    sub.plan = "basic"
    sub.status = "active"
    sub.starts_at = datetime.now(timezone.utc)
    sub.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    sub.monthly_amount = 9900
    sub.toss_billing_key = "tb_mock_key"
    sub.toss_customer_key = str(sub.user_id)
    sub.cancelled_at = None
    return sub


class TestSubscriptionService:

    @pytest.fixture
    def service(self, mock_db):
        return SubscriptionService(mock_db)

    def test_get_plans_4개_플랜_반환(self, service):
        plans = service.get_plans()
        assert len(plans) == 4
        plan_dict = {p.id: p for p in plans}
        assert "starter" in plan_dict
        assert "basic" in plan_dict
        assert "standard" in plan_dict
        assert "premium" in plan_dict

    def test_get_plans_가격_확인(self, service):
        plans = service.get_plans()
        plan_dict = {p.id: p for p in plans}
        assert plan_dict["starter"].price == 0
        assert plan_dict["basic"].price == 9900
        assert plan_dict["standard"].price == 29000
        assert plan_dict["premium"].price == 49000

    async def test_get_my_subscription_활성_구독_조회(self, service, mock_user, mock_subscription):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=mock_subscription)
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_current_usage = AsyncMock(return_value={
            "chat_count": 5, "contract_count": 2, "payslip_send_count": 3
        })

        result = await service.get_my_subscription(mock_user)
        assert result.subscription is not None
        assert result.subscription.plan == "basic"
        assert result.subscription.status == "active"
        assert result.usage.chat_count == 5

    async def test_get_my_subscription_구독_없음(self, service, mock_user):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=None)
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_current_usage = AsyncMock(return_value={
            "chat_count": 0, "contract_count": 0, "payslip_send_count": 0
        })

        result = await service.get_my_subscription(mock_user)
        assert result.subscription is None
        assert result.usage.chat_count == 0

    async def test_create_subscription_이미_활성_구독_존재(self, service, mock_user, mock_subscription):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=mock_subscription)

        with pytest.raises(SubscriptionActiveError):
            await service.create_subscription(mock_user, plan="basic", billing_key="tb_valid")

    async def test_create_subscription_유효하지_않은_빌링키(self, service, mock_user):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=None)

        with pytest.raises(BillingKeyInvalidError):
            await service.create_subscription(mock_user, plan="basic", billing_key="tb_invalid_key")

    async def test_change_plan_동일_플랜_실패(self, service, mock_user, mock_subscription):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=mock_subscription)

        with pytest.raises(SubscriptionActiveError):
            await service.change_plan(mock_user, new_plan="basic")

    async def test_change_plan_활성_구독_없음(self, service, mock_user):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=None)

        with pytest.raises(SubscriptionNotFoundError):
            await service.change_plan(mock_user, new_plan="standard")

    async def test_cancel_subscription_이미_해지됨(self, service, mock_user):
        service.subscription_repo = AsyncMock()
        service.subscription_repo.get_active_by_user = AsyncMock(return_value=None)

        with pytest.raises(SubscriptionNotFoundError):
            await service.cancel_subscription(mock_user, reason="테스트")

    def test_calculate_proration_비례_계산(self, service):
        result = service.calculate_proration(
            current_plan="basic", new_plan="standard", remaining_days=15
        )
        assert result == 9550

    def test_calculate_proration_월_초_변경(self, service):
        result = service.calculate_proration(
            current_plan="basic", new_plan="standard", remaining_days=30
        )
        assert result == 19100


class TestPlanService:

    @pytest.fixture
    def service(self, mock_db):
        return PlanService(mock_db)

    def test_check_feature_access_스타터_채팅_허용(self, service, mock_user):
        mock_user.plan = "free"
        mock_user.plan_expires_at = None
        assert service.check_feature_access(mock_user, feature="chat") is True

    def test_check_feature_access_스타터_급여계산_거부(self, service, mock_user):
        mock_user.plan = "free"
        mock_user.plan_expires_at = None
        assert service.check_feature_access(mock_user, feature="payroll") is False

    def test_check_feature_access_베이직_급여계산_허용(self, service, mock_user):
        mock_user.plan = "basic"
        mock_user.plan_expires_at = None
        assert service.check_feature_access(mock_user, feature="payroll") is True

    def test_check_feature_access_만료된_플랜_거부(self, service, mock_user):
        mock_user.plan = "basic"
        mock_user.plan_expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        assert service.check_feature_access(mock_user, feature="chat") is False

    async def test_check_usage_limit_스타터_채팅_5회_사용_허용(self, service, mock_user):
        mock_user.plan = "free"
        mock_user.plan_expires_at = None
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_current_usage = AsyncMock(return_value={"chat_count": 5})

        result = await service.check_usage_limit(mock_user, usage_type="chat")
        assert result["allowed"] is True
        assert result["remaining"] == 5

    async def test_check_usage_limit_스타터_채팅_10회_도달_거부(self, service, mock_user):
        mock_user.plan = "free"
        mock_user.plan_expires_at = None
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_current_usage = AsyncMock(return_value={"chat_count": 10})

        result = await service.check_usage_limit(mock_user, usage_type="chat")
        assert result["allowed"] is False
        assert result["remaining"] == 0

    async def test_check_usage_limit_프리미엄_무제한(self, service, mock_user):
        mock_user.plan = "premium"
        mock_user.plan_expires_at = None
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_current_usage = AsyncMock(return_value={"chat_count": 100})

        result = await service.check_usage_limit(mock_user, usage_type="chat")
        assert result["allowed"] is True
        assert result["remaining"] is None

    async def test_increment_usage_사용량_증가(self, service, mock_user):
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_or_create = AsyncMock(return_value=MagicMock())
        service.plan_usage_repo.increment = AsyncMock()

        await service.increment_usage(mock_user, usage_type="chat")
        service.plan_usage_repo.increment.assert_called_once()

    async def test_get_current_usage_현재_사용량_조회(self, service, mock_user):
        service.plan_usage_repo = AsyncMock()
        service.plan_usage_repo.get_current_usage = AsyncMock(return_value={
            "chat_count": 5, "contract_count": 2, "payslip_send_count": 10,
            "attorney_consult_count": 0
        })

        result = await service.get_current_usage(mock_user)
        assert result["chat_count"] == 5
        assert result["contract_count"] == 2
        assert result["payslip_send_count"] == 10

    def test_get_plan_features_스타터_기능_조회(self, service):
        features = service.get_plan_features(plan="free")
        assert features["chat_limit"] == 10
        assert features["contract_limit"] == 2
        assert features["payroll"] is False

    def test_get_plan_features_프리미엄_기능_조회(self, service):
        features = service.get_plan_features(plan="premium")
        assert features["chat_limit"] is None
        assert features["payroll"] is True
        assert features["attorney_consult"] is True
        assert features["attorney_consult_limit"] == 1
