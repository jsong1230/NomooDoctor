# 퇴직금/해고 API 라우터
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.schemas.severance import (
    SeveranceCalculateRequest,
    SeveranceCalculateResponse,
    SeveranceResponse,
    SeveranceSummary,
    TerminationGuideRequest,
    TerminationGuideResponse,
    DocumentGenerateRequest,
    DocumentGenerateResponse,
)
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_redis, get_current_company_id
from app.core.rate_limit import check_rate_limit
from app.services.severance_service import SeveranceService
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post(
    "/calculate",
    response_model=ApiResponse[SeveranceCalculateResponse],
    status_code=status.HTTP_200_OK,
    summary="퇴직금 시뮬레이션",
    description="퇴직금을 시뮬레이션합니다 (미리보기, DB 저장 안 함)",
)
async def calculate_severance(
    request: SeveranceCalculateRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """퇴직금 시뮬레이션

    퇴직금을 실시간으로 계산합니다 (미리보기용, DB 저장 없음).
    """
    # Rate Limit 체크 (30회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:calculate_severance:{user_id}",
        limit=30,
        window_seconds=3600,
    )

    service = SeveranceService(db)
    result = await service.calculate_severance(
        db, UUID(company_id), request
    )

    return ApiResponse(
        data=result,
        meta={"message": "퇴직금이 계산되었습니다."},
    )


@router.post(
    "/severance",
    response_model=ApiResponse[SeveranceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="퇴직금 확정 저장",
    description="계산된 퇴직금을 확정하여 DB에 저장합니다.",
)
async def create_severance(
    request: SeveranceCalculateRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """퇴직금 확정 저장

    계산된 퇴직금을 확정하여 DB에 저장합니다.
    """
    # Rate Limit 체크 (10회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:create_severance:{user_id}",
        limit=10,
        window_seconds=3600,
    )

    service = SeveranceService(db)
    result = await service.create_severance(
        db, UUID(company_id), request
    )

    return ApiResponse(
        data=result,
        meta={"message": "퇴직금이 저장되었습니다."},
    )


@router.get(
    "/severance/{severance_id}",
    response_model=ApiResponse[SeveranceResponse],
    summary="퇴직금 상세 조회",
    description="저장된 퇴직금 기록을 조회합니다.",
)
async def get_severance(
    severance_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """퇴직금 상세 조회

    저장된 퇴직금 기록의 상세 정보를 조회합니다.
    """
    # Rate Limit 체크
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_severance:{user_id}",
        limit=100,
        window_seconds=60,
    )

    service = SeveranceService(db)
    repo = service.severance_repo

    record = await repo.get_by_id_and_company(UUID(severance_id), UUID(company_id))
    if not record:
        raise NotFoundError(
            message="퇴직금 기록을 찾을 수 없습니다.",
            code="E-5013",
        )

    # 응답 구성
    return ApiResponse(
        data=SeveranceResponse(
            id=str(record.id),
            employee_id=str(record.employee_id),
            employee_name="",  # 실제로는 직원 정보 조회 필요
            hire_date=record.hire_date,
            resign_date=record.resign_date,
            total_service_days=record.total_service_days,
            average_daily_wage=int(record.average_daily_wage),
            severance_pay=int(record.severance_pay),
            unused_leave_pay=int(record.unused_leave_pay),
            bonus_included=0,  # 실제로는 계산 결과에서 추출
            total_payment=int(record.total_payment),
            payment_deadline=record.payment_deadline,
            eligible=True,
            calculation_detail={
                "last_3_months_total_wage": record.calculation_detail.get("last_3_months_total_wage", 0) if record.calculation_detail else 0,
                "last_3_months_total_days": record.calculation_detail.get("last_3_months_total_days", 0) if record.calculation_detail else 0,
                "bonus_3_months_share": record.calculation_detail.get("bonus_3_months_share", 0) if record.calculation_detail else 0,
                "average_daily_wage": int(record.average_daily_wage),
                "severance_formula": "",
                "unused_leave_formula": "",
            },
            status=record.status,
            created_at=record.created_at,
        )
    )


@router.get(
    "/severance",
    response_model=ApiResponse[list[SeveranceSummary]],
    summary="퇴직금 목록 조회",
    description="사업장의 퇴직금 기록 목록을 조회합니다.",
)
async def list_severances(
    employee_id: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    req: Request = None,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """퇴직금 목록 조회

    사업장의 퇴직금 기록 목록을 조회합니다.
    """
    # Rate Limit 체크
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:list_severances:{user_id}",
        limit=100,
        window_seconds=60,
    )

    service = SeveranceService(db)
    repo = service.severance_repo

    records = await repo.list_by_company(
        UUID(company_id),
        UUID(employee_id) if employee_id else None,
        status,
        limit,
        offset,
    )

    # 응답 구성
    summaries = [
        SeveranceSummary(
            id=str(r.id),
            employee_id=str(r.employee_id),
            employee_name="",  # 실제로는 직원 정보 조회 필요
            resign_date=r.resign_date,
            total_payment=int(r.total_payment),
            status=r.status,
            payment_deadline=r.payment_deadline,
            created_at=r.created_at,
        )
        for r in records
    ]

    return ApiResponse(
        data=summaries,
        meta={"total": len(summaries), "limit": limit, "offset": offset},
    )


@router.post(
    "/termination-guide",
    response_model=ApiResponse[TerminationGuideResponse],
    summary="해고 절차 가이드 생성",
    description="Claude API를 활용한 해고/퇴직 절차 가이드를 생성합니다.",
)
async def generate_termination_guide(
    request: TerminationGuideRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """해고 절차 가이드 생성

    해고/퇴직 절차 가이드를 생성합니다.
    """
    # Rate Limit 체크 (10회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:termination_guide:{user_id}",
        limit=10,
        window_seconds=3600,
    )

    service = SeveranceService(db)
    result = await service.generate_termination_guide(
        db, UUID(company_id), request
    )

    return ApiResponse(
        data=result,
        meta={"message": "해고 절차 가이드가 생성되었습니다."},
    )


@router.post(
    "/documents/generate",
    response_model=ApiResponse[DocumentGenerateResponse],
    summary="해고 서류 생성",
    description="해고예고통지서 또는 권고사직서를 생성합니다.",
)
async def generate_document(
    request: DocumentGenerateRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """해고 서류 생성

    해고예고통지서 또는 권고사직서를 생성합니다.
    """
    # Rate Limit 체크 (10회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:document_generate:{user_id}",
        limit=10,
        window_seconds=3600,
    )

    # 실제 구현에서는 Claude API 호출 및 PDF 생성
    # 여기서는 모의 구현
    mock_url = f"https://s3.example.com/documents/{request.document_type}_{UUID(user_id)}.pdf"
    expires_at = __import__("datetime").datetime.utcnow() + __import__("datetime").timedelta(hours=24)

    return ApiResponse(
        data=DocumentGenerateResponse(
            download_url=mock_url,
            expires_at=expires_at,
            filename=f"{request.document_type}_document.pdf",
            document_type=request.document_type,
        ),
        meta={"message": "서류가 생성되었습니다."},
    )
