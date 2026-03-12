# Subscription 모델
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class Subscription(Base):
    """구독 모델"""
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    toss_customer_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    toss_billing_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    toss_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monthly_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    payments: Mapped[list["PaymentHistory"]] = relationship(
        "PaymentHistory", back_populates="subscription", cascade="all, delete-orphan"
    )


class PaymentHistory(Base):
    """결제 이력 모델"""
    __tablename__ = "payment_history"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    toss_payment_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True
    )
    toss_order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    refund_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_metadata: Mapped[dict[str, int] | None] = mapped_column("metadata", JSON, nullable=True)  # type: ignore
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="payments")
    user: Mapped["User"] = relationship("User", back_populates="payment_history")


class PlanUsage(Base):
    """플랜 사용량 모델"""
    __tablename__ = "plan_usage"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    usage_month: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )  # first day of month
    chat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    contract_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payslip_send_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attorney_consult_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="plan_usage")


# Indexes
Index("idx_subscriptions_user_status", Subscription.user_id, Subscription.status)
Index(
    "idx_subscriptions_expires_active",
    Subscription.expires_at,
    postgresql_where=Subscription.status == "active"
)
Index("idx_payment_history_user", PaymentHistory.user_id, PaymentHistory.created_at.desc())
Index("idx_payment_history_subscription", PaymentHistory.subscription_id)
Index("idx_payment_history_toss_order", PaymentHistory.toss_order_id)
Index("idx_plan_usage_user_month", PlanUsage.user_id, PlanUsage.usage_month, unique=True)

# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
