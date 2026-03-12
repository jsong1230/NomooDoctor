# 노무사 마켓플레이스 모델
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, Text, Numeric, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base
import uuid


class LaborAttorney(Base):
    """파트너 노무사"""
    __tablename__ = "labor_attorneys"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    firm_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    specialties: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    regions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    consultation_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), nullable=False, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    response_rate: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="attorney_profile")
    cases: Mapped[list["AttorneyCase"]] = relationship(
        "AttorneyCase", back_populates="attorney", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["AttorneyReview"]] = relationship(
        "AttorneyReview", back_populates="attorney", cascade="all, delete-orphan"
    )


class AttorneyCase(Base):
    """노무사 상담 케이스"""
    __tablename__ = "attorney_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    attorney_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("labor_attorneys.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )
    chat_session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True
    )
    case_summary: Mapped[str] = mapped_column(Text, nullable=False)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    consultation_type: Mapped[str] = mapped_column(String(20), nullable=False, default="video")
    preferred_schedule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fee_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

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
    user: Mapped["User"] = relationship("User", back_populates="attorney_cases")
    attorney: Mapped["LaborAttorney"] = relationship("LaborAttorney", back_populates="cases")
    review: Mapped["AttorneyReview | None"] = relationship(
        "AttorneyReview", back_populates="case", uselist=False
    )


class AttorneyReview(Base):
    """노무사 리뷰"""
    __tablename__ = "attorney_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attorney_cases.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    attorney_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("labor_attorneys.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    case: Mapped["AttorneyCase"] = relationship("AttorneyCase", back_populates="review")
    user: Mapped["User"] = relationship("User")
    attorney: Mapped["LaborAttorney"] = relationship("LaborAttorney", back_populates="reviews")


# Indexes
Index("idx_attorneys_rating", LaborAttorney.rating.desc())
Index("idx_cases_user", AttorneyCase.user_id, AttorneyCase.created_at.desc())
Index("idx_cases_attorney", AttorneyCase.attorney_id)
Index("idx_reviews_attorney", AttorneyReview.attorney_id)

# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
