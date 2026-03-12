"""급여 관련 스키마"""
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Any


class PayrollCalculateRequest(BaseModel):
    """급여 계산 요청"""
    employee_id: str = Field(..., description="직원 ID")
    pay_year: int = Field(..., ge=2020, le=2099, description="급여 연도")
    pay_month: int = Field(..., ge=1, le=12, description="급여 월")
    base_wage: Decimal = Field(..., gt=0, description="기본급")
    overtime_minutes: int = Field(default=0, ge=0, description="연장근무 시간(분)")
    night_minutes: int = Field(default=0, ge=0, description="야간근무 시간(분)")
    holiday_minutes: int = Field(default=0, ge=0, description="휴일근무 시간(분)")
    meal_allowance: Decimal = Field(default=0, ge=0, description="식대")
    transport_allowance: Decimal = Field(default=0, ge=0, description="교통비")
    income_tax_family_count: int = Field(default=1, ge=1, le=10, description="소득세 가족 수")


class PayrollCalculateResponse(BaseModel):
    """급여 계산 응답"""
    # 지급 항목
    employee_id: str
    pay_year: int
    pay_month: int
    base_wage: int
    overtime_pay: int
    night_pay: int
    holiday_pay: int
    meal_allowance: int
    transport_allowance: int
    total_gross: int
    # 공제 항목
    national_pension: int
    health_insurance: int
    long_term_care: int
    employment_insurance: int
    income_tax: int
    local_income_tax: int
    total_deduction: int
    # 실수령액
    net_pay: int


class PayrollRatesResponse(BaseModel):
    """급여 요율 응답"""
    # 사회보험 요율
    national_pension_rate: str  # "0.045" (4.5%)
    health_insurance_rate: str  # "0.03545" (3.545%)
    long_term_care_rate: str  # "0.1295" (12.95%)
    employment_insurance_rate: str  # "0.009" (0.9%)
    local_income_tax_rate: str  # "0.1" (10%)
    # 근로기준법 요율
    overtime_rate: str  # "1.5" (1.5배)
    night_rate: str  # "0.5" (0.5배 추가)
    holiday_rate_normal: str  # "1.5" (8시간 이내 1.5배)
    holiday_rate_over: str  # "2.0" (8시간 초과 2.0배)
