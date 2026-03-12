# Compliance API 라우터 — 컴플라이언스 대시보드
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.compliance import (
    RiskScoreResponse,
    ComplianceEventsResponse,
    UpcomingEventsResponse,
    RiskScoreHistoryResponse,
)
from app.core.dependencies import get_current_user_id, get_current_company_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.compliance_service import ComplianceService
from datetime import date
import uuid

router = APIRouter()


@router.get(
    "/score",
    response_model=ApiResponse[dict],
    summary="리스크 스코어 조회",
    description="사업장의 컴플라이언스 리스크 스코어를 조회합니다.",
)
async def get_risk_score(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    리스크 스코어 조회

    기본 100점에서 감점 방식으로 계산합니다.
    - 근로계약서 미작성: -10점/인
    - 취업규칙 미작성 (10인 이상): -20점
    - 급여명세서 미발송: -5점/인

    색상 구분:
    - green: 80~100점
    - yellow: 60~79점
    - red: 0~59점
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:compliance_score:{user_id}:{company_id}",
        limit=100,
        window_seconds=60,
    )

    service = ComplianceService(db)
    result = await service.calculate_risk_score(company_id=uuid.UUID(company_id))

    return ApiResponse(data=result)


@router.get(
    "/details",
    response_model=ApiResponse[dict],
    summary="리스크 상세 항목 조회",
    description="리스크 스코어의 상세 감점 항목을 조회합니다.",
)
async def get_risk_details(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    리스크 상세 항목 조회

    감점 항목별 위반 내용과 해결 방법을 조회합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:compliance_details:{user_id}:{company_id}",
        limit=100,
        window_seconds=60,
    )

    service = ComplianceService(db)
    score_data = await service.calculate_risk_score(company_id=uuid.UUID(company_id))

    return ApiResponse(data={
        "score": score_data["score"],
        "level": score_data["level"],
        "details": score_data["details"],
    })


@router.get(
    "/events",
    response_model=ApiResponse[dict],
    summary="노무 이벤트 목록 (캘린더용)",
    description="지정 연월의 노무 이벤트 목록을 반환합니다.",
)
async def get_compliance_events(
    req: Request,
    year: int = Query(default=None, ge=2020, le=2100, description="조회 연도"),
    month: int = Query(default=None, ge=1, le=12, description="조회 월"),
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    노무 이벤트 목록 (캘린더용)

    - 계약 만료일
    - 급여 지급일
    """
    # 기본값: 현재 연월
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:compliance_events:{user_id}:{company_id}",
        limit=100,
        window_seconds=60,
    )

    service = ComplianceService(db)
    events = await service.get_compliance_events(
        company_id=uuid.UUID(company_id),
        year=year,
        month=month,
    )

    return ApiResponse(data={
        "events": events,
        "year": year,
        "month": month,
    })


@router.get(
    "/events/upcoming",
    response_model=ApiResponse[dict],
    summary="향후 이벤트 조회",
    description="D-30, D-7 등 향후 이벤트 목록을 반환합니다.",
)
async def get_upcoming_events(
    req: Request,
    days: int = Query(default=30, ge=1, le=365, description="조회 기간 (일)"),
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    향후 이벤트 조회

    계약 만료 D-30, D-7 등 알림이 필요한 이벤트를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:compliance_upcoming:{user_id}:{company_id}",
        limit=100,
        window_seconds=60,
    )

    service = ComplianceService(db)
    events = await service.get_upcoming_events(
        company_id=uuid.UUID(company_id),
        days=days,
    )

    return ApiResponse(data={
        "events": events,
        "period_days": days,
    })


@router.get(
    "/score/history",
    response_model=ApiResponse[dict],
    summary="월별 리스크 스코어 변화",
    description="월별 리스크 스코어 변화 그래프 데이터를 반환합니다.",
)
async def get_risk_score_history(
    req: Request,
    months: int = Query(default=6, ge=1, le=12, description="조회 개월 수"),
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    월별 리스크 스코어 변화

    프론트엔드 그래프 렌더링용 데이터를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:compliance_history:{user_id}:{company_id}",
        limit=100,
        window_seconds=60,
    )

    service = ComplianceService(db)
    history = await service.get_risk_score_history(
        company_id=uuid.UUID(company_id),
        months=months,
    )

    return ApiResponse(data={"history": history})
