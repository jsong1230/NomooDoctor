# Employees API 라우터
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post("/", response_model=ApiResponse[EmployeeResponse], status_code=201)
async def create_employee(
    request: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    직원 등록

    새로운 직원을 등록합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "직원 등록 기능은 구현 중입니다."}
    )


@router.get("/", response_model=PaginatedResponse[EmployeeListResponse])
async def list_employees(
    company_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    직원 목록 조회

    사업장의 직원 목록을 반환합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=[],
        meta=PaginationMeta(page=page, per_page=per_page, total=0)
    )


@router.get("/{employee_id}", response_model=ApiResponse[EmployeeResponse])
async def get_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    직원 상세 조회

    특정 직원의 상세 정보를 반환합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "직원 상세 조회 기능은 구현 중입니다."}
    )


@router.patch("/{employee_id}", response_model=ApiResponse[EmployeeResponse])
async def update_employee(
    employee_id: str,
    request: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    직원 정보 수정

    특정 직원의 정보를 수정합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "직원 정보 수정 기능은 구현 중입니다."}
    )


@router.delete("/{employee_id}", response_model=ApiResponse[dict])
async def delete_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    직원 삭제

    특정 직원을 삭제합니다.
    """
    # TODO: 구현 필요
    return ApiResponse(
        data=None,
        meta={"message": "직원 삭제 기능은 구현 중입니다."}
    )
