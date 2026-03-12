# Contract 관련 스키마
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, validator
import uuid


class ContractBase(BaseModel):
    """Contract 기본 스키마"""
    employee_id: uuid.UUID
    contract_type: Literal["regular", "fixed_term", "part_time", "daily", "probation", "foreign_worker"]
    start_date: date
    end_date: date | None = None
    work_location: str = Field(..., min_length=1, max_length=500)
    work_hours_per_week: float = Field(..., gt=0, le=52)
    work_start_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    work_end_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    break_minutes: int = Field(default=60, ge=0, le=180)
    work_days: str = Field(..., min_length=1, max_length=20)
    wage_type: Literal["monthly", "hourly", "daily"]
    base_wage: int = Field(..., gt=0)
    meal_allowance: int = Field(default=0, ge=0)
    transport_allowance: int = Field(default=0, ge=0)
    probation_months: int = Field(default=0, ge=0)
    probation_wage_rate: float = Field(default=1.0, gt=0, le=1.0)
    nda_included: bool = False
    non_compete_included: bool = False


class ContractCreate(ContractBase):
    """Contract 생성"""
    pass


class ContractResponse(ContractBase):
    """Contract 응답"""
    id: uuid.UUID
    company_id: uuid.UUID
    status: str
    docx_url: str | None
    pdf_url: str | None
    ai_generated: bool
    ai_model: str | None
    signed_at: str | None
    sign_service_ref: str | None
    version: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    """Contract 목록 응답 (간단)"""
    id: uuid.UUID
    employee_id: uuid.UUID
    employee_name: str | None
    contract_type: str
    start_date: date
    status: str
    created_at: str
