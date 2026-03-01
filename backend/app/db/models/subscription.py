# Subscription 모델
from datetime import datetime
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    toss_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    toss_billing_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    monthly_amount: Mapped[float] = mapped_column(Numeric(10, 0), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint(
            "plan IN ('free', 'basic', 'standard', 'premium', 'enterprise')",
            name="ck_subscription_plan"
        ),
        CheckConstraint(
            "status IN ('active', 'cancelled', 'expired', 'paused')",
            name="ck_subscription_status"
        ),
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_expires", "expires_at"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
