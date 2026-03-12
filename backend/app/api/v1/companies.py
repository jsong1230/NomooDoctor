# Companies API 라우터
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyDeleteRequest,
    CompanySelectRequest,
    CompanyListResponse,
    CompanySelectResponse,
)
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.company_service import CompanyService
from app.core.security import decode_token
import uuid

router = APIRouter()


@router.post(
    "/",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="사업장 등록",
    description="새로운 사업장을 등록합니다."
)
async def create_company(
    request: CompanyCreate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    사업장 등록

    새로운 사업장을 등록합니다.
    """
    # Rate Limit 체크 (10회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:create_company:{user_id}",
        limit=10,
        window_seconds=3600
    )

    company_service = CompanyService(db, redis)

    result = await company_service.create_company(
        owner_id=uuid.UUID(user_id),
        business_name=request.business_name,
        business_number=request.business_number,
        representative_name=request.representative_name,
        industry_type=request.industry_type,
        employee_count=request.employee_count,
        address=request.address,
        postal_code=request.postal_code,
        phone=request.phone
    )

    return ApiResponse(data=result, meta={"message": "사업장이 등록되었습니다."})


@router.get(
    "/",
    response_model=CompanyListResponse,
    summary="사업장 목록 조회",
    description="사용자의 사업장 목록을 반환합니다."
)
async def list_companies(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    limit: int = 20,
    cursor: str | None = None,
    is_deleted: bool = False,
):
    """
    사업장 목록 조회

    사용자의 사업장 목록을 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:list_companies:{user_id}",
        limit=100,
        window_seconds=60
    )

    company_service = CompanyService(db, redis)

    result = await company_service.get_companies(
        owner_id=uuid.UUID(user_id),
        limit=limit,
        cursor=cursor,
        is_deleted=is_deleted
    )

    return CompanyListResponse(**result)


@router.get(
    "/{company_id}",
    response_model=ApiResponse[dict],
    summary="사업장 상세 조회",
    description="특정 사업장의 상세 정보를 반환합니다."
)
async def get_company(
    company_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    사업장 상세 조회

    특정 사업장의 상세 정보를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_company:{user_id}",
        limit=100,
        window_seconds=60
    )

    company_service = CompanyService(db, redis)

    result = await company_service.get_company(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id)
    )

    return ApiResponse(data=result)


@router.put(
    "/{company_id}",
    response_model=ApiResponse[dict],
    summary="사업장 정보 수정",
    description="특정 사업장의 정보를 수정합니다."
)
async def update_company(
    company_id: str,
    request: CompanyUpdate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    사업장 정보 수정

    특정 사업장의 정보를 수정합니다.
    """
    # Rate Limit 체크 (30회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:update_company:{user_id}:{company_id}",
        limit=30,
        window_seconds=3600
    )

    company_service = CompanyService(db, redis)

    result = await company_service.update_company(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        business_name=request.business_name,
        representative_name=request.representative_name,
        industry_type=request.industry_type,
        employee_count=request.employee_count,
        address=request.address,
        postal_code=request.postal_code,
        phone=request.phone
    )

    return ApiResponse(data=result, meta={"message": "사업장 정보가 수정되었습니다."})


@router.delete(
    "/{company_id}",
    response_model=ApiResponse[dict],
    summary="사업장 삭제",
    description="특정 사업장을 삭제합니다 (Soft Delete)."
)
async def delete_company(
    company_id: str,
    request: CompanyDeleteRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    사업장 삭제

    특정 사업장을 삭제합니다 (Soft Delete).
    """
    # Rate Limit 체크 (5회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:delete_company:{user_id}",
        limit=5,
        window_seconds=3600
    )

    company_service = CompanyService(db, redis)

    await company_service.delete_company(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        confirmation=request.confirmation
    )

    return ApiResponse(
        data=None,
        meta={"message": "사업장이 삭제되었습니다. 30일 이내에 복구 가능합니다."}
    )


@router.post(
    "/{company_id}/select",
    response_model=ApiResponse[dict],
    summary="사업장 선택",
    description="현재 사업장을 선택합니다 (컨텍스트 변경)."
)
async def select_company(
    company_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    request: CompanySelectRequest | None = None,
):
    """
    사업장 선택

    현재 사업장을 선택합니다 (컨텍스트 변경).
    """
    # Rate Limit 체크 (30회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:select_company:{user_id}",
        limit=30,
        window_seconds=3600
    )

    # 현재 토큰에서 user_plan, user_role 추출
    # Authorization 헤더에서 토큰 추출
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    payload = decode_token(token)
    user_plan = payload.get("plan", "free")
    user_role = payload.get("role", "owner")

    company_service = CompanyService(db, redis)

    result = await company_service.select_company(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        user_plan=user_plan,
        user_role=user_role
    )

    return ApiResponse(
        data={
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": result["token_type"],
            "expires_in": result["expires_in"],
            "company": result["company"]
        },
        meta={"message": "사업장이 선택되었습니다."}
    )
