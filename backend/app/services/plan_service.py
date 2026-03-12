# Plan Service
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.subscription import PlanUsage
from app.repositories.plan_usage_repo import PlanUsageRepository
from app.core.exceptions import PlanUpgradeRequiredError


class PlanService:
    """플랜 서비스"""

    PLAN_LIMITS: Dict[str, Dict[str, Any]] = {
        "free": {
            "chat_limit": 10,
            "contract_limit": 2,
            "payroll": False,
            "payslip_send_limit": 0,
            "attorney_consult": False,
        },
        "basic": {
            "chat_limit": None,
            "contract_limit": None,
            "payroll": True,
            "payslip_send_limit": 10,
            "attorney_consult": False,
        },
        "standard": {
            "chat_limit": None,
            "contract_limit": None,
            "payroll": True,
            "payslip_send_limit": 100,
            "attorney_consult": False,
        },
        "premium": {
            "chat_limit": None,
            "contract_limit": None,
            "payroll": True,
            "payslip_send_limit": None,
            "attorney_consult": True,
            "attorney_consult_limit": 1,
        },
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_usage_repo = PlanUsageRepository(db)

    # ===== 기능 접근 제어 =====

    def check_feature_access(self, user: User, feature: str) -> bool:
        """
        기능 접근 권한 확인

        Args:
            user: 사용자
            feature: 기능명 (chat, contract, payroll, payslip_send, attorney_consult)

        Returns:
            접근 허용 여부
        """
        # 사용자 플랜 확인
        plan = user.plan

        # 만료된 플랜인지 확인
        if user.plan_expires_at and user.plan_expires_at < datetime.now(timezone.utc):
            return False

        # 플랜별 기능 제한 확인
        limits = self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS["free"])

        if feature in ("chat", "contract"):
            # chat과 contract는 모든 플랜에서 접근 가능 (사용량 제한은 별도 확인)
            return True
        elif feature == "payroll":
            return limits["payroll"]
        elif feature == "payslip_send":
            return limits["payslip_send_limit"] is None or limits["payslip_send_limit"] > 0
        elif feature == "attorney_consult":
            return limits["attorney_consult"]

        return False

    async def check_usage_limit(
        self,
        user: User,
        usage_type: str
    ) -> Dict[str, Any]:
        """
        사용량 제한 확인

        Args:
            user: 사용자
            usage_type: 사용 타입 (chat, contract, payslip_send, attorney_consult)

        Returns:
            제한 결과
        """
        plan = user.plan
        limits = self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS["free"])

        # 만료된 플랜
        if user.plan_expires_at and user.plan_expires_at < datetime.now(timezone.utc):
            return {
                "allowed": False,
                "remaining": 0,
                "limit": None
            }

        # 무제한 플랜
        if limits.get(f"{usage_type}_limit") is None:
            return {
                "allowed": True,
                "remaining": None,
                "limit": None
            }

        # 사용량 조회
        usage = await self.plan_usage_repo.get_current_usage(user.id)
        current_count = usage.get(f"{usage_type}_count", 0)
        limit = limits.get(f"{usage_type}_limit", 0)

        # 제한 확인
        if current_count >= limit:
            return {
                "allowed": False,
                "remaining": 0,
                "limit": limit
            }

        return {
            "allowed": True,
            "remaining": limit - current_count,
            "limit": limit
        }

    async def increment_usage(
        self,
        user: User,
        usage_type: str
    ) -> None:
        """
        사용량 증가

        Args:
            user: 사용자
            usage_type: 사용 타입
        """
        usage = await self.plan_usage_repo.get_or_create(
            user.id,
            datetime.now(timezone.utc)
        )
        await self.plan_usage_repo.increment(usage, usage_type)

    async def get_current_usage(self, user: User) -> Dict[str, Any]:
        """현재 월 사용량 조회"""
        usage = await self.plan_usage_repo.get_current_usage(user.id)

        plan = user.plan
        limits = self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS["free"])

        return {
            "chat_count": usage.get("chat_count", 0),
            "chat_limit": limits.get("chat_limit"),
            "contract_count": usage.get("contract_count", 0),
            "contract_limit": limits.get("contract_limit"),
            "payslip_send_count": usage.get("payslip_send_count", 0),
            "payslip_send_limit": limits.get("payslip_send_limit"),
            "attorney_consult_count": usage.get("attorney_consult_count", 0),
            "attorney_consult_limit": limits.get("attorney_consult_limit"),
        }

    # ===== 플랜 기능 반환 =====

    def get_plan_features(self, plan: str) -> Dict[str, Any]:
        """플랜별 기능 반환"""
        limits = self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS["free"])
        return limits

    def get_plan_name(self, plan: str) -> str:
        """플랜 이름 반환"""
        PLAN_NAMES = {
            "free": "스타터",
            "basic": "베이직",
            "standard": "스탠다드",
            "premium": "프리미엄",
        }
        return PLAN_NAMES.get(plan, "알 수 없음")

    def get_plan_price(self, plan: str) -> int:
        """플랜 가격 반환"""
        PLAN_PRICES = {
            "free": 0,
            "basic": 9900,
            "standard": 29000,
            "premium": 49000,
        }
        return PLAN_PRICES.get(plan, 0)
