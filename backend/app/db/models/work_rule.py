# WorkRule 모델
from datetime import datetime, date
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class WorkRule(Base):
    __tablename__ = "work_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    industry_type: Mapped[str] = mapped_column(String(50), default="other", nullable=False)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    revision_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    total_worker_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_docx_url: Mapped[str | None] = mapped_column(String, nullable=True)
    docx_url: Mapped[str | None] = mapped_column(String, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(nullable=True)
    approval_date: Mapped[date | None] = mapped_column(nullable=True)
    worker_consent_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'under_review', 'active', 'superseded')",
            name="ck_workrule_status"
        ),
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="work_rules")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .company import Company
