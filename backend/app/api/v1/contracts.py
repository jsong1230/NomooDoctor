# Contracts API 라우터
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.contract import ContractCreate, ContractResponse, SignRequestCreate
from app.schemas.common import ApiResponse, ErrorResponse
from app.core.dependencies import get_current_user_id, get_current_company_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.contract_service import ContractService
from app.core.exceptions import ValidationError, NotFoundError, AppError
from pydantic import BaseModel, Field
import uuid


router = APIRouter()


@router.post(
    "/",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="계약서 초안 생성",
    description="새로운 근로계약서 초안을 생성합니다."
)
async def create_contract(
    request: ContractCreate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    계약서 초안 생성

    새로운 근로계약서 초안을 생성합니다.
    """
    # Rate Limit 체크 (20회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:create_contract:{user_id}:{company_id}",
        limit=20,
        window_seconds=3600
    )

    contract_service = ContractService(db, redis)

    try:
        result = await contract_service.create_contract(
            company_id=uuid.UUID(company_id),
            user_id=uuid.UUID(user_id),
            employee_id=request.employee_id,
            contract_type=request.contract_type,
            start_date=request.start_date,
            end_date=request.end_date,
            work_location=request.work_location,
            work_hours_per_week=request.work_hours_per_week,
            work_start_time=request.work_start_time,
            work_end_time=request.work_end_time,
            break_minutes=request.break_minutes,
            work_days=request.work_days,
            wage_type=request.wage_type,
            base_wage=request.base_wage,
            meal_allowance=request.meal_allowance,
            transport_allowance=request.transport_allowance,
            probation_months=request.probation_months,
            probation_wage_rate=request.probation_wage_rate,
            nda_included=request.nda_included,
            non_compete_included=request.non_compete_included
        )

        return ApiResponse(data=result, meta={"message": "계약서 초안이 생성되었습니다."})
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error={
                    "code": "E-5001",
                    "message": e.message,
                    "details": e.details
                }
            ).model_dump()
        )


@router.get(
    "/",
    response_model=ApiResponse[list],
    summary="계약서 목록 조회",
    description="사업장의 계약서 목록을 반환합니다."
)
async def list_contracts(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    employee_id: str | None = None,
    status_filter: str | None = None,
    page: int = 1,
    per_page: int = 20,
):
    """
    계약서 목록 조회

    사업장의 계약서 목록을 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:list_contracts:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    contract_service = ContractService(db, redis)

    per_page = min(per_page, 100)  # 최대 100개 제한
    skip = (page - 1) * per_page

    employee_uuid = uuid.UUID(employee_id) if employee_id else None

    result = await contract_service.get_contracts(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        employee_id=employee_uuid,
        status=status_filter,
        limit=per_page,
        skip=skip
    )

    return ApiResponse(data=result)


@router.get(
    "/{contract_id}",
    response_model=ApiResponse[dict],
    summary="계약서 상세 조회",
    description="특정 계약서의 상세 정보를 반환합니다."
)
async def get_contract(
    contract_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    계약서 상세 조회

    특정 계약서의 상세 정보를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_contract:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    contract_service = ContractService(db, redis)

    try:
        result = await contract_service.get_contract(
            contract_id=uuid.UUID(contract_id),
            company_id=uuid.UUID(company_id),
            user_id=uuid.UUID(user_id)
        )

        return ApiResponse(data=result)
    except NotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error={
                    "code": e.code,
                    "message": e.message
                }
            ).model_dump()
        )


# === 전자서명 ===

@router.post(
    "/{contract_id}/sign-request",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="전자서명 요청",
    description="계약서에 대한 전자서명 요청을 발송합니다."
)
async def send_sign_request(
    contract_id: str,
    request: SignRequestCreate,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """전자서명 요청 발송"""
    contract_service = ContractService(db, redis)
    try:
        result = await contract_service.send_sign_request(
            contract_id=uuid.UUID(contract_id),
            company_id=uuid.UUID(company_id),
            user_id=uuid.UUID(user_id),
            signer_name=request.signer_name,
            signer_email=request.signer_email,
            signer_phone=request.signer_phone,
        )
        return ApiResponse(data=result)
    except NotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(error={"code": e.code, "message": e.message}).model_dump()
        )
    except AppError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(error={"code": e.code, "message": e.message}).model_dump()
        )


@router.get(
    "/{contract_id}/sign-status",
    response_model=ApiResponse[dict],
    summary="서명 상태 조회",
)
async def get_sign_status(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """전자서명 상태 조회"""
    contract_service = ContractService(db, redis)
    try:
        result = await contract_service.get_sign_status(
            contract_id=uuid.UUID(contract_id),
            company_id=uuid.UUID(company_id),
            user_id=uuid.UUID(user_id),
        )
        return ApiResponse(data=result)
    except NotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(error={"code": e.code, "message": e.message}).model_dump()
        )


@router.get(
    "/{contract_id}/signed-pdf",
    summary="서명된 PDF 다운로드",
)
async def download_signed_pdf(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """서명 완료된 PDF 다운로드"""
    contract_service = ContractService(db, redis)
    try:
        pdf_bytes = await contract_service.get_signed_pdf(
            contract_id=uuid.UUID(contract_id),
            company_id=uuid.UUID(company_id),
            user_id=uuid.UUID(user_id),
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}_signed.pdf"},
        )
    except NotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(error={"code": e.code, "message": e.message}).model_dump()
        )
    except AppError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(error={"code": e.code, "message": e.message}).model_dump()
        )
