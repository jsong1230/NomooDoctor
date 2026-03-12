# Salary 관련 모델 (SalarySetting, WorkRecord, Payslip)
from datetime import datetime, date, time
from sqlalchemy import (
    String, Integer, Text, Date, Time, Boolean, DateTime, ForeignKey,
    CheckConstraint, Index, Numeric
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class SalarySetting(Base):
    __tablename__ = "salary_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    wage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_wage: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    meal_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    transport_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    income_tax_family_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint(
            "wage_type IN ('monthly', 'hourly', 'daily')",
            name="ck_salary_wage_type"
        ),
        Index("idx_salary_settings_employee", "employee_id", "effective_from"),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="salary_settings")


class WorkRecord(Base):
    __tablename__ = "work_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_start: Mapped[time] = mapped_column(Time, nullable=False)
    scheduled_end: Mapped[time] = mapped_column(Time, nullable=False)
    actual_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    actual_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_minutes: Mapped[int] = mapped_column(Integer, default=60)
    overtime_minutes: Mapped[int] = mapped_column(Integer, default=0)
    night_minutes: Mapped[int] = mapped_column(Integer, default=0)
    holiday_minutes: Mapped[int] = mapped_column(Integer, default=0)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Indexes
    __table_args__ = (
        Index("idx_work_records_employee_date", "employee_id", "work_date"),
        Index("idx_work_records_company_date", "company_id", "work_date"),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="work_records")


class Payslip(Base):
    __tablename__ = "payslips"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    pay_year: Mapped[int] = mapped_column(Integer, nullable=False)
    pay_month: Mapped[int] = mapped_column(Integer, nullable=False)
    # 지급
    base_pay: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    holiday_pay: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    overtime_pay: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    night_pay: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    holiday_work_pay: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    meal_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    transport_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    other_allowance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    gross_pay: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    # 공제
    national_pension: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    health_insurance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    long_term_care: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    employment_insurance: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    income_tax: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    local_income_tax: Mapped[float] = mapped_column(Numeric(10, 0), default=0)
    total_deduction: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    net_pay: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    # 발송
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_via: Mapped[str | None] = mapped_column(String(20), nullable=True)
    send_status: Mapped[str] = mapped_column(String(20), default="pending")
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 메타
    calculation_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint("pay_month BETWEEN 1 AND 12", name="ck_payslip_month"),
        CheckConstraint(
            "send_status IN ('pending', 'sent', 'failed')",
            name="ck_send_status"
        ),
        Index("idx_payslips_unique", "employee_id", "pay_year", "pay_month", unique=True),
        Index("idx_payslips_company_period", "company_id", "pay_year", "pay_month"),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="payslips")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .employee import Employee
