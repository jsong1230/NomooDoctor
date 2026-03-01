# Company 관련 스키마
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
import uuid


class CompanyBase(BaseModel):
    """Company 기본 스키마"""
    business_name: str = Field(..., min_length=1, max_length=200)
    business_number: str = Field(..., pattern=r"^\d{3}-\d{2}-\d{5}$")
    representative_name: str = Field(..., min_length=1, max_length=100)
    industry_type: Literal["manufacturing", "food_service", "retail", "service", "it", "construction", "healthcare", "other"]
    employee_count: int = Field(..., ge=0, le=1000)
    address: str | None = None
    postal_code: str | None = None
    phone: str | None = None


class CompanyCreate(CompanyBase):
    """Company 생성"""
    pass


class CompanyUpdate(BaseModel):
    """Company 수정"""
    business_name: str | None = Field(None, min_length=1, max_length=200)
    representative_name: str | None = Field(None, min_length=1, max_length=100)
    industry_type: Literal["manufacturing", "food_service", "retail", "service", "it", "construction", "healthcare", "other"] | None = None
    employee_count: int | None = Field(None, ge=0, le=1000)
    address: str | None = None
    postal_code: str | None = None
    phone: str | None = None


class CompanyResponse(CompanyBase):
    """Company 응답"""
    id: uuid.UUID
    owner_id: uuid.UUID
    work_rule_required: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
