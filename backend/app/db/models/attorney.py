# Attorney 관련 모델 (LaborAttorney, AttorneyCase)
from datetime import datetime
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class LaborAttorney(Base):
    __tablename__ = "labor_attorneys"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    firm_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    specialties: Mapped[list[str]] = mapped_column(Text, nullable=False)
    regions: Mapped[list[str]] = mapped_column(Text, nullable=False)
    consultation_fee: Mapped[float] = mapped_column(Numeric(10, 0), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0.00)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    response_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    cases: Mapped[list["AttorneyCase"]] = relationship("AttorneyCase", back_populates="attorney", cascade="all, delete-orphan")


class AttorneyCase(Base):
    __tablename__ = "attorney_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    attorney_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labor_attorneys.id"), nullable=False)
    company_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    case_summary: Mapped[str] = mapped_column(Text, nullable=False)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fee_amount: Mapped[float | None] = mapped_column(Numeric(10, 0), nullable=True)
    fee_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    fee_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "urgency IN ('low', 'medium', 'high', 'emergency')",
            name="ck_urgency"
        ),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'in_progress', 'completed', 'cancelled')",
            name="ck_case_status"
        ),
        CheckConstraint(
            "consultation_type IN ('phone', 'video', 'visit')",
            name="ck_consultation_type"
        ),
    )

    # Relationships
    attorney: Mapped["LaborAttorney"] = relationship("LaborAttorney", back_populates="cases")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .company import Company
