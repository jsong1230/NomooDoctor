# Employee 관련 스키마
from datetime import datetime, date
from typing import Literal
from pydantic import BaseModel, Field
import uuid


class EmployeeBase(BaseModel):
    """Employee 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100)
    nationality: Literal["korean", "chinese", "vietnamese", "american", "other"] = "korean"
    employment_type: Literal["regular", "fixed_term", "part_time", "daily", "dispatch", "probation"]
    department: str | None = None
    position: str | None = None
    hire_date: date
    phone: str | None = None
    email: str | None = None
    bank_name: str | None = None
    bank_account: str | None = None


class EmployeeCreate(EmployeeBase):
    """Employee 생성"""
    id_number: str | None = None


class EmployeeUpdate(BaseModel):
    """Employee 수정"""
    name: str | None = Field(None, min_length=1, max_length=100)
    department: str | None = None
    position: str | None = None
    phone: str | None = None
    email: str | None = None
    bank_name: str | None = None
    bank_account: str | None = None
    is_active: bool | None = None


class EmployeeResponse(EmployeeBase):
    """Employee 응답"""
    id: uuid.UUID
    company_id: uuid.UUID
    user_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Employee 목록 응답 (간단)"""
    id: uuid.UUID
    name: str
    employment_type: str
    is_active: bool
    hire_date: date
