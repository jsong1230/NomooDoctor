# Subscription API Router
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.subscription import (
    CreateSubscriptionRequest,
    ChangePlanRequest,
    CancelSubscriptionRequest,
    RegisterBillingKeyRequest,
)
from app.schemas.common import ApiResponse
from app.db.models.user import User
from app.core.dependencies import get_current_user
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/subscriptions", tags=["구독"])


# ===== 플랜 목록 =====
@router.get("/plans")
async def get_plans():
    """플랜 목록 조회"""
    service = SubscriptionService(None)
    plans = service.get_plans()
    return ApiResponse(
        data={
            "plans": [plan.model_dump() for plan in plans]
        }
    )


# ===== 내 구독 정보 =====
@router.get("/me")
async def get_my_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """내 구독 정보 조회"""
    service = SubscriptionService(db)
    result = await service.get_my_subscription(user)
    return ApiResponse(data=result.model_dump())


# ===== 구독 생성 =====
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """구독 생성"""
    service = SubscriptionService(db)
    result = await service.create_subscription(user, request.plan, request.billing_key)
    return ApiResponse(data=result.model_dump())


# ===== 플랜 변경 =====
@router.put("")
async def change_plan(
    request: ChangePlanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """플랜 변경"""
    service = SubscriptionService(db)
    result = await service.change_plan(user, request.plan)
    return ApiResponse(data=result.model_dump())


# ===== 구독 해지 =====
@router.delete("")
async def cancel_subscription(
    request: CancelSubscriptionRequest = CancelSubscriptionRequest(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """구독 해지"""
    service = SubscriptionService(db)
    result = await service.cancel_subscription(
        user,
        reason=request.reason,
        feedback=request.feedback
    )
    return ApiResponse(data=result.model_dump())


# ===== 빌링키 등록 =====
@router.post("/billing-key")
async def register_billing_key(
    request: RegisterBillingKeyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """빌링키 등록"""
    service = PaymentService(db)
    result = await service.register_billing_key(user, request.auth_key, request.customer_key)
    return ApiResponse(data=result.model_dump())


# ===== 결제 내역 =====
@router.get("/history")
async def get_payment_history(
    limit: int = 20,
    cursor: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """결제 내역 조회"""
    service = PaymentService(db)
    result = await service.get_payment_history(user, limit, cursor)
    return ApiResponse(data=result)
