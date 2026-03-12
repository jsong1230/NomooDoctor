# Severance 관련 모델 (SeveranceRecord, TerminationDocument)
from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Date, DateTime, ForeignKey, CheckConstraint, Index, Boolean, Text, Numeric
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class SeveranceRecord(Base):
    __tablename__ = "severance_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    resign_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_service_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_3m_total_wage: Mapped[float] = mapped_column(Numeric(14, 0), nullable=False)
    last_3m_total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus_3m_share: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    average_daily_wage: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    severance_pay: Mapped[float] = mapped_column(Numeric(14, 0), nullable=False)
    unused_leave_days: Mapped[int] = mapped_column(Integer, default=0)
    unused_leave_pay: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    total_payment: Mapped[float] = mapped_column(Numeric(14, 0), nullable=False)
    payment_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="calculated", nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    calculation_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint("status IN ('calculated', 'paid', 'overdue')", name="ck_severance_status"),
        Index("idx_severance_employee", "employee_id"),
        Index("idx_severance_company", "company_id"),
        Index("idx_severance_unique", "employee_id", "resign_date", unique=True),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="severance_records")


class TerminationDocument(Base):
    __tablename__ = "termination_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    termination_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    docx_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('dismissal_notice', 'resignation_agreement')",
            name="ck_termination_doc_type"
        ),
        Index("idx_termination_docs_employee", "employee_id"),
        Index("idx_termination_docs_company", "company_id"),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="termination_documents")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .employee import Employee
