# Payslips API 라우터
from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.payslip import PayslipCreate, PayslipResponse, SendPayslipRequest
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_current_company_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.payslip_service import PayslipService
import uuid
import io

router = APIRouter()


@router.post(
    "/",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="급여명세서 생성",
    description="새로운 급여명세서를 생성합니다."
)
async def create_payslip(
    request: PayslipCreate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    급여명세서 생성

    새로운 급여명세서를 생성합니다.
    """
    # Rate Limit 체크 (50회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:create_payslip:{user_id}:{company_id}",
        limit=50,
        window_seconds=3600
    )

    payslip_service = PayslipService(db)

    result = await payslip_service.create_payslip(
        company_id=uuid.UUID(company_id),
        employee_id=request.employee_id,
        year=request.year,
        month=request.month,
        base_salary=request.base_salary,
        weekly_allowance=request.weekly_allowance,
        overtime_pay=request.overtime_pay,
        night_pay=request.night_pay,
        holiday_pay=request.holiday_pay,
        meal_allowance=request.meal_allowance,
        transport_allowance=request.transport_allowance,
        national_pension=request.national_pension,
        health_insurance=request.health_insurance,
        long_term_care=request.long_term_care,
        employment_insurance=request.employment_insurance,
        income_tax=request.income_tax,
        local_income_tax=request.local_income_tax,
    )

    return ApiResponse(data=result, meta={"message": "급여명세서가 생성되었습니다."})


@router.get(
    "/",
    response_model=ApiResponse[list],
    summary="급여명세서 목록 조회",
    description="사업장의 급여명세서 목록을 반환합니다."
)
async def list_payslips(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    year: int | None = None,
    month: int | None = None,
    employee_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
):
    """
    급여명세서 목록 조회

    사업장의 급여명세서 목록을 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:list_payslips:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    payslip_service = PayslipService(db)

    per_page = min(per_page, 100)  # 최대 100개 제한

    result = await payslip_service.list_payslips(
        company_id=uuid.UUID(company_id),
        year=year,
        month=month,
        employee_id=uuid.UUID(employee_id) if employee_id else None,
        page=page,
        per_page=per_page,
    )

    return ApiResponse(data=result)


@router.get(
    "/{payslip_id}",
    response_model=ApiResponse[dict],
    summary="급여명세서 상세 조회",
    description="특정 급여명세서의 상세 정보를 반환합니다."
)
async def get_payslip(
    payslip_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    급여명세서 상세 조회

    특정 급여명세서의 상세 정보를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_payslip:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    payslip_service = PayslipService(db)

    result = await payslip_service.get_payslip(
        payslip_id=uuid.UUID(payslip_id),
        company_id=uuid.UUID(company_id),
    )

    return ApiResponse(data=result)


@router.get(
    "/{payslip_id}/pdf",
    summary="급여명세서 PDF 다운로드",
    description="급여명세서를 PDF로 다운로드합니다."
)
async def get_payslip_pdf(
    payslip_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    급여명세서 PDF 다운로드

    급여명세서를 PDF 형식으로 다운로드합니다.
    """
    # Rate Limit 체크 (50회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_payslip_pdf:{user_id}:{company_id}",
        limit=50,
        window_seconds=3600
    )

    payslip_service = PayslipService(db)

    pdf_content = await payslip_service.get_payslip_pdf(
        payslip_id=uuid.UUID(payslip_id),
        company_id=uuid.UUID(company_id),
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=payslip_{payslip_id}.pdf"
        }
    )


@router.post(
    "/{payslip_id}/send",
    response_model=ApiResponse[dict],
    summary="급여명세서 발송",
    description="급여명세서를 이메일 또는 카카오 알림톡으로 발송합니다."
)
async def send_payslip(
    payslip_id: str,
    request: SendPayslipRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    급여명세서 발송

    급여명세서를 이메일 또는 카카오 알림톡으로 발송합니다.
    """
    # Rate Limit 체크 (30회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:send_payslip:{user_id}:{company_id}",
        limit=30,
        window_seconds=3600
    )

    payslip_service = PayslipService(db)

    result = await payslip_service.send_payslip(
        payslip_id=uuid.UUID(payslip_id),
        company_id=uuid.UUID(company_id),
        method=request.method,
        email=request.email,
    )

    return ApiResponse(data=result, meta={"message": "급여명세서가 발송되었습니다."})
