# Employees API 라우터
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_current_company_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.employee_service import EmployeeService
from app.services.payslip_service import PayslipService
from app.core.exceptions import ValidationError
import uuid

router = APIRouter()


@router.post(
    "/",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="직원 등록",
    description="새로운 직원을 등록합니다."
)
async def create_employee(
    request: EmployeeCreate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    직원 등록

    새로운 직원을 등록합니다.
    """
    # Rate Limit 체크 (20회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:create_employee:{user_id}:{company_id}",
        limit=20,
        window_seconds=3600
    )

    employee_service = EmployeeService(db, redis)

    result = await employee_service.create_employee(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        name=request.name,
        id_number=request.id_number,
        nationality=request.nationality,
        employment_type=request.employment_type,
        department=request.department,
        position=request.position,
        hire_date=request.hire_date,
        phone=request.phone,
        email=request.email,
        bank_name=request.bank_name,
        bank_account=request.bank_account
    )

    return ApiResponse(data=result, meta={"message": "직원이 등록되었습니다."})


@router.get(
    "/",
    response_model=ApiResponse[list],
    summary="직원 목록 조회",
    description="사업장의 직원 목록을 반환합니다."
)
async def list_employees(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    is_active: bool | None = None,
    page: int = 1,
    per_page: int = 20,
):
    """
    직원 목록 조회

    사업장의 직원 목록을 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:list_employees:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    employee_service = EmployeeService(db, redis)

    per_page = min(per_page, 100)  # 최대 100개 제한
    skip = (page - 1) * per_page

    result = await employee_service.get_employees(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        is_active=is_active,
        limit=per_page,
        skip=skip
    )

    return ApiResponse(data=result)


@router.get(
    "/{employee_id}",
    response_model=ApiResponse[dict],
    summary="직원 상세 조회",
    description="특정 직원의 상세 정보를 반환합니다."
)
async def get_employee(
    employee_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    직원 상세 조회

    특정 직원의 상세 정보를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_employee:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    employee_service = EmployeeService(db, redis)

    result = await employee_service.get_employee(
        employee_id=uuid.UUID(employee_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id)
    )

    return ApiResponse(data=result)


@router.patch(
    "/{employee_id}",
    response_model=ApiResponse[dict],
    summary="직원 정보 수정",
    description="특정 직원의 정보를 수정합니다."
)
async def update_employee(
    employee_id: str,
    request: EmployeeUpdate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    직원 정보 수정

    특정 직원의 정보를 수정합니다.
    """
    # Rate Limit 체크 (30회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:update_employee:{user_id}:{company_id}:{employee_id}",
        limit=30,
        window_seconds=3600
    )

    employee_service = EmployeeService(db, redis)

    result = await employee_service.update_employee(
        employee_id=uuid.UUID(employee_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        name=request.name,
        department=request.department,
        position=request.position,
        phone=request.phone,
        email=request.email,
        bank_name=request.bank_name,
        bank_account=request.bank_account,
        is_active=request.is_active
    )

    return ApiResponse(data=result, meta={"message": "직원 정보가 수정되었습니다."})


@router.patch(
    "/{employee_id}/resign",
    response_model=ApiResponse[dict],
    summary="직원 퇴직 처리",
    description="특정 직원을 퇴직 처리합니다 (Soft Delete)."
)
async def resign_employee(
    employee_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    직원 퇴직 처리

    특정 직원을 퇴직 처리합니다 (Soft Delete).
    """
    # Rate Limit 체크 (10회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:resign_employee:{user_id}:{company_id}",
        limit=10,
        window_seconds=3600
    )

    employee_service = EmployeeService(db, redis)

    result = await employee_service.resign_employee(
        employee_id=uuid.UUID(employee_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id)
    )

    return ApiResponse(data=result, meta={"message": "직원이 퇴직 처리되었습니다."})


@router.delete(
    "/{employee_id}",
    response_model=ApiResponse[dict],
    summary="직원 삭제 (예약)",
    description="직원 삭제는 지원하지 않습니다. 퇴직 처리를 사용하세요."
)
async def delete_employee(
    employee_id: str,
    req: Request,
):
    """
    직원 삭제 (예약)

    직원 삭제는 지원하지 않습니다. 퇴직 처리를 사용하세요.
    """
    raise ValidationError(
        message="직원 삭제는 지원하지 않습니다.",
        details=[{"message": "퇴직 처리 API를 사용해주세요: PATCH /api/v1/employees/{id}/resign"}]
    )


@router.get(
    "/{employee_id}/payslips",
    response_model=ApiResponse[list],
    summary="직원 급여 히스토리 조회",
    description="특정 직원의 급여명세서 히스토리를 반환합니다."
)
async def get_employee_payslips(
    employee_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    limit: int = 24,
):
    """
    직원 급여 히스토리 조회

    특정 직원의 급여명세서 히스토리를 반환합니다.
    """
    # Rate Limit 체크 (100회/분)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:get_employee_payslips:{user_id}:{company_id}",
        limit=100,
        window_seconds=60
    )

    payslip_service = PayslipService(db)

    result = await payslip_service.list_employee_payslips(
        employee_id=uuid.UUID(employee_id),
        company_id=uuid.UUID(company_id),
        limit=min(limit, 60),
    )

    return ApiResponse(data=result)
