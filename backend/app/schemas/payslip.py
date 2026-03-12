# Payslip 관련 스키마
from datetime import datetime, date
from typing import Literal
from pydantic import BaseModel, Field
from decimal import Decimal
import uuid


class PayslipCreate(BaseModel):
    """급여명세서 생성 요청"""
    employee_id: uuid.UUID
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    payment_date: date
    # 지급 항목
    base_salary: Decimal = Field(..., ge=0)
    weekly_allowance: Decimal = Field(default=Decimal("0"), ge=0)
    overtime_pay: Decimal = Field(default=Decimal("0"), ge=0)
    night_pay: Decimal = Field(default=Decimal("0"), ge=0)
    holiday_pay: Decimal = Field(default=Decimal("0"), ge=0)
    meal_allowance: Decimal = Field(default=Decimal("0"), ge=0)
    transport_allowance: Decimal = Field(default=Decimal("0"), ge=0)
    # 공제 항목
    national_pension: Decimal = Field(default=Decimal("0"), ge=0)
    health_insurance: Decimal = Field(default=Decimal("0"), ge=0)
    long_term_care: Decimal = Field(default=Decimal("0"), ge=0)
    employment_insurance: Decimal = Field(default=Decimal("0"), ge=0)
    income_tax: Decimal = Field(default=Decimal("0"), ge=0)
    local_income_tax: Decimal = Field(default=Decimal("0"), ge=0)


class PayslipResponse(BaseModel):
    """급여명세서 응답"""
    id: uuid.UUID
    employee_id: uuid.UUID
    employee_name: str
    company_name: str
    year: int
    month: int
    payment_date: date | None = None
    # 지급 항목
    base_salary: Decimal
    weekly_allowance: Decimal
    overtime_pay: Decimal
    night_pay: Decimal
    holiday_pay: Decimal
    meal_allowance: Decimal
    transport_allowance: Decimal
    total_payment: Decimal
    # 공제 항목
    national_pension: Decimal
    health_insurance: Decimal
    long_term_care: Decimal
    employment_insurance: Decimal
    income_tax: Decimal
    local_income_tax: Decimal
    total_deduction: Decimal
    # 실수령액
    net_salary: Decimal
    # 발송 상태
    send_status: str
    sent_at: datetime | None = None
    sent_via: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PayslipListResponse(BaseModel):
    """급여명세서 목록 응답"""
    id: uuid.UUID
    employee_id: uuid.UUID
    employee_name: str
    year: int
    month: int
    net_salary: Decimal
    send_status: str
    created_at: datetime


class SendPayslipRequest(BaseModel):
    """급여명세서 발송 요청"""
    method: Literal["email", "kakao", "both"] = "email"
    email: str | None = None
