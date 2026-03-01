# Contract 모델
from datetime import datetime, date, time
from sqlalchemy import (
    String, Integer, Text, Date, Time, Boolean, DateTime, ForeignKey,
    CheckConstraint, Index, Numeric, JSONB
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(30), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    work_location: Mapped[str] = mapped_column(Text, nullable=False)
    work_hours_per_week: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    work_start_time: Mapped[time] = mapped_column(Time, nullable=False)
    work_end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    work_days: Mapped[str] = mapped_column(String(20), nullable=False)
    wage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_wage: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    meal_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    transport_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    probation_months: Mapped[int] = mapped_column(Integer, default=0)
    probation_wage_rate: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0)
    nda_included: Mapped[bool] = mapped_column(Boolean, default=False)
    non_compete_included: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    docx_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sign_service_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    expiry_notice_30_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    expiry_notice_7_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint(
            "contract_type IN ('regular', 'fixed_term', 'part_time', 'daily', 'probation', 'foreign_worker')",
            name="ck_contract_type"
        ),
        CheckConstraint(
            "wage_type IN ('monthly', 'hourly', 'daily')",
            name="ck_wage_type"
        ),
        CheckConstraint(
            "status IN ('draft', 'sent', 'signed', 'expired', 'terminated')",
            name="ck_status"
        ),
        Index("idx_contracts_employee_id", "employee_id"),
        Index("idx_contracts_company_id", "company_id"),
        Index("idx_contracts_end_date", "end_date"),
        Index("idx_contracts_status", "status"),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="contracts")
    company: Mapped["Company"] = relationship("Company", back_populates="contracts")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .employee import Employee
    from .company import Company
