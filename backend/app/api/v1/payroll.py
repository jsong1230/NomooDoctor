"""F-05 급여 자동 계산기 API 라우터"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id, get_current_company_id, get_db
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.schemas.payroll import (
    PayrollCalculateRequest,
    PayrollCalculateResponse,
    PayrollRatesResponse,
)
from app.schemas.common import ApiResponse
from app.services.payroll_service import PayrollService


router = APIRouter()


@router.post("/calculate", response_model=ApiResponse[dict])
async def calculate_payroll(
    request: PayrollCalculateRequest,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
):
    """
    급여 계산 API

    - base_wage: 기본급
    - overtime_minutes: 연장근무 시간(분)
    - night_minutes: 야간근무 시간(분)
    - holiday_minutes: 휴일근무 시간(분)
    - meal_allowance: 식대
    - transport_allowance: 교통비
    - income_tax_family_count: 소득세 가족 수
    """
    # 직원 접근 권한 확인
    employee = await PayrollService.verify_employee_access(
        db, company_id, request.employee_id
    )

    # 급여 계산
    payroll_result = PayrollService.calculate_payroll(
        employee_id=request.employee_id,
        pay_year=request.pay_year,
        pay_month=request.pay_month,
        base_wage=request.base_wage,
        overtime_minutes=request.overtime_minutes,
        night_minutes=request.night_minutes,
        holiday_minutes=request.holiday_minutes,
        meal_allowance=request.meal_allowance,
        transport_allowance=request.transport_allowance,
        income_tax_family_count=request.income_tax_family_count,
    )

    return ApiResponse(data=payroll_result)


@router.get("/rates", response_model=ApiResponse[dict])
async def get_payroll_rates(
    user_id: str = Depends(get_current_user_id),
):
    """
    급여 요율 조회 API

    - 국민연금, 건강보험, 장기요양보험, 고용보험 요율
    - 연장수당, 야간수당, 휴일수당 비율
    """
    rates = PayrollService.get_rates()
    return ApiResponse(data=rates)
