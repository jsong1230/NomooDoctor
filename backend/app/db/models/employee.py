# Employee 모델
from datetime import datetime, date
from sqlalchemy import String, Integer, Text, Date, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    id_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), default="korean", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    resign_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint(
            "nationality IN ('korean', 'chinese', 'vietnamese', 'american', 'other')",
            name="ck_employee_nationality"
        ),
        CheckConstraint(
            "employment_type IN ('regular', 'fixed_term', 'part_time', 'daily', 'dispatch', 'probation')",
            name="ck_employee_employment_type"
        ),
        Index("idx_employees_company_id", "company_id"),
        Index("idx_employees_hire_date", "hire_date"),
        Index("idx_employees_is_active", "company_id", "is_active"),
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="employees")
    user: Mapped["User | None"] = relationship("User")
    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="employee", cascade="all, delete-orphan")
    salary_settings: Mapped[list["SalarySetting"]] = relationship("SalarySetting", back_populates="employee", cascade="all, delete-orphan")
    work_records: Mapped[list["WorkRecord"]] = relationship("WorkRecord", back_populates="employee", cascade="all, delete-orphan")
    payslips: Mapped[list["Payslip"]] = relationship("Payslip", back_populates="employee", cascade="all, delete-orphan")
    severance_records: Mapped[list["SeveranceRecord"]] = relationship("SeveranceRecord", back_populates="employee", cascade="all, delete-orphan")
    termination_documents: Mapped[list["TerminationDocument"]] = relationship("TerminationDocument", back_populates="employee", cascade="all, delete-orphan")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .company import Company
    from .user import User
    from .contract import Contract
    from .salary import SalarySetting, WorkRecord, Payslip
    from .severance import SeveranceRecord, TerminationDocument
