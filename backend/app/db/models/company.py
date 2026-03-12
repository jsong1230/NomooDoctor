# Company 모델
from datetime import datetime
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import uuid


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_number: Mapped[str] = mapped_column(String(20), nullable=False)
    representative_name: Mapped[str] = mapped_column(String(100), nullable=False)
    industry_type: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    work_rule_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default="false")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint(
            "industry_type IN ('manufacturing', 'food_service', 'retail', 'service', 'it', 'construction', 'healthcare', 'other')",
            name="ck_company_industry_type"
        ),
        CheckConstraint(
            "work_rule_required = (employee_count >= 10)",
            name="ck_company_work_rule_required"
        ),
        Index("idx_companies_owner_id", "owner_id"),
        Index("idx_companies_business_number", "business_number", unique=True),
        Index("idx_companies_owner_id_active", "owner_id"),
        Index("idx_companies_is_deleted", "is_deleted"),
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="companies")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="company", cascade="all, delete-orphan")
    work_rules: Mapped[list["WorkRule"]] = relationship("WorkRule", back_populates="company", cascade="all, delete-orphan")


# Import 후방 참조 해결
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .employee import Employee
    from .contract import Contract
    from .work_rule import WorkRule
