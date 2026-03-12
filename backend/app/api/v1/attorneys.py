# 노무사 마켓플레이스 API
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.attorney import CreateCaseRequest, CreateReviewRequest
from app.services.attorney_service import AttorneyService

router = APIRouter()


# === 노무사 프로필 (공개) ===

@router.get("/attorneys")
async def list_attorneys(
    specialty: Optional[str] = None,
    region: Optional[str] = None,
    sort: str = "rating",
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """노무사 목록 조회"""
    service = AttorneyService(db)
    result = await service.list_attorneys(
        specialty=specialty, region=region, sort=sort, limit=limit, offset=offset
    )
    return ApiResponse(data=result)


@router.get("/attorneys/{attorney_id}")
async def get_attorney(
    attorney_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """노무사 상세 조회"""
    service = AttorneyService(db)
    result = await service.get_attorney(attorney_id)
    return ApiResponse(data=result.model_dump())


# === 상담 케이스 (인증 필요) ===

@router.post("/attorney-cases", status_code=status.HTTP_201_CREATED)
async def create_case(
    request: CreateCaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """상담 신청"""
    service = AttorneyService(db)
    result = await service.create_case(user, request)
    return ApiResponse(data=result.model_dump())


@router.get("/attorney-cases")
async def list_my_cases(
    case_status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 상담 케이스 목록"""
    service = AttorneyService(db)
    result = await service.list_my_cases(user, status=case_status, limit=limit, offset=offset)
    return ApiResponse(data=result)


@router.get("/attorney-cases/{case_id}")
async def get_case(
    case_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """케이스 상세 조회"""
    service = AttorneyService(db)
    result = await service.get_case(user, case_id)
    return ApiResponse(data=result.model_dump())


@router.put("/attorney-cases/{case_id}/cancel")
async def cancel_case(
    case_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """케이스 취소"""
    service = AttorneyService(db)
    result = await service.cancel_case(user, case_id)
    return ApiResponse(data=result)


# === 리뷰 ===

@router.post("/attorney-cases/{case_id}/review", status_code=status.HTTP_201_CREATED)
async def create_review(
    case_id: UUID,
    request: CreateReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """리뷰 작성"""
    service = AttorneyService(db)
    result = await service.create_review(user, case_id, request)
    return ApiResponse(data=result.model_dump())


@router.get("/attorneys/{attorney_id}/reviews")
async def list_reviews(
    attorney_id: UUID,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """노무사 리뷰 목록"""
    service = AttorneyService(db)
    result = await service.list_reviews(attorney_id, limit=limit, offset=offset)
    return ApiResponse(data=result)
