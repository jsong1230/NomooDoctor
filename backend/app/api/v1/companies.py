# Companies API 라우터
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post("/", response_model=ApiResponse[CompanyResponse], status_code=201)
async def create_company(
    request: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    사업장 등록

    새로운 사업장을 등록합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "사업장 등록 기능은 구현 중입니다."}
    )


@router.get("/", response_model=PaginatedResponse[CompanyResponse])
async def list_companies(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    사업장 목록 조회

    사용자의 사업장 목록을 반환합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=[],
        meta=PaginationMeta(page=page, per_page=per_page, total=0)
    )


@router.get("/{company_id}", response_model=ApiResponse[CompanyResponse])
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    사업장 상세 조회

    특정 사업장의 상세 정보를 반환합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "사업장 상세 조회 기능은 구현 중입니다."}
    )


@router.patch("/{company_id}", response_model=ApiResponse[CompanyResponse])
async def update_company(
    company_id: str,
    request: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    사업장 정보 수정

    특정 사업장의 정보를 수정합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "사업장 정보 수정 기능은 구현 중입니다."}
    )


@router.delete("/{company_id}", response_model=ApiResponse[dict])
async def delete_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    사업장 삭제

    특정 사업장을 삭제합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "사업장 삭제 기능은 구현 중입니다."}
    )
