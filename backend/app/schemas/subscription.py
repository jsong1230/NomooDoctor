# Subscription 스키마
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


# ===== 플랜 관련 =====
class PlanFeature(BaseModel):
    """플랜 기능"""
    chat_limit: Optional[int] = None
    contract_limit: Optional[int] = None
    payroll: bool = False
    payslip_send_limit: Optional[int] = 0
    attorney_consult: bool = False
    attorney_consult_limit: Optional[int] = None


class PlanInfo(BaseModel):
    """플랜 정보"""
    id: str
    name: str
    price: int
    features: PlanFeature


# ===== 구독 관련 =====
class SubscriptionResponse(BaseModel):
    """구독 응답"""
    id: UUID
    plan: str
    status: str
    starts_at: datetime
    expires_at: Optional[datetime]
    monthly_amount: int
    has_billing_key: bool
    cancelled_at: Optional[datetime]


class UsageInfo(BaseModel):
    """사용량 정보"""
    month: str
    chat_count: int
    contract_count: int
    payslip_send_count: int
    chat_limit: Optional[int]
    contract_limit: Optional[int]
    payslip_send_limit: Optional[int]


class MySubscriptionResponse(BaseModel):
    """내 구독 응답"""
    subscription: Optional[SubscriptionResponse]
    usage: UsageInfo


# ===== 구독 생성/변경 =====
class CreateSubscriptionRequest(BaseModel):
    """구독 생성 요청"""
    plan: str
    billing_key: str
    success_url: Optional[str] = None
    fail_url: Optional[str] = None


class ChangePlanRequest(BaseModel):
    """플랜 변경 요청"""
    plan: str


class SubscriptionResult(BaseModel):
    """구독 결과"""
    subscription_id: UUID
    toss_order_id: str
    status: str
    starts_at: datetime
    expires_at: datetime


class PlanChangeResult(BaseModel):
    """플랜 변경 결과"""
    subscription_id: UUID
    old_plan: str
    new_plan: str
    proration_amount: int
    proration_description: str
    next_billing_amount: int
    effective_at: datetime


class CancelSubscriptionRequest(BaseModel):
    """구독 해지 요청"""
    reason: Optional[str] = None
    feedback: Optional[str] = None


class CancelSubscriptionResult(BaseModel):
    """구독 해지 결과"""
    subscription_id: UUID
    status: str
    cancelled_at: datetime
    access_until: datetime
    message: str


# ===== 빌링키 관련 =====
class BillingKeyResponse(BaseModel):
    """빌링키 응답"""
    billing_key: str
    card_company: str
    card_number: str
    card_type: str
    registered_at: datetime


class RegisterBillingKeyRequest(BaseModel):
    """빌링키 등록 요청"""
    auth_key: str
    customer_key: str


# ===== 결제 이력 =====
class PaymentHistoryItem(BaseModel):
    """결제 이력 항목"""
    id: UUID
    toss_payment_id: Optional[str]
    amount: int
    status: str
    payment_method: Optional[str]
    paid_at: Optional[datetime]


class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""
    cursor: Optional[str] = None
    has_next: bool
    limit: int
    total_count: int


class PaymentHistoryResponse(BaseModel):
    """결제 이력 응답"""
    payments: List[PaymentHistoryItem]
    pagination: PaginationMeta


# ===== 웹훅 =====
class TossWebhookPayload(BaseModel):
    """토스 웹훅 페이로드"""
    eventType: str
    data: dict


# ===== 사용량 제한 =====
class UsageLimitResult(BaseModel):
    """사용량 제한 결과"""
    allowed: bool
    remaining: Optional[int]
    limit: Optional[int]
