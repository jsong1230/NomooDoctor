# 근태 관리 API
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.attendance import (
    WorkRecordCreate,
    WorkRecordUpdate,
    WorkRecordBatchCreate,
    WorkRecordResponse,
    ImportResultResponse,
    MonthlySummaryResponse,
    EmployeeAnalysisResponse,
)
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_current_company_id
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.services.attendance_service import AttendanceService
from app.services.excel_import_service import ExcelImportService

router = APIRouter()


@router.post(
    "/records",
    response_model=ApiResponse[WorkRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="근무 기록 생성",
    description="새로운 근무 기록을 생성합니다."
)
async def create_work_record(
    request: WorkRecordCreate,
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """근무 기록 생성"""
    service = AttendanceService(db)

    try:
        record = await service.create_record(
            company_id=UUID(company_id),
            employee_id=request.employee_id,
            work_date=request.work_date,
            scheduled_start=request.scheduled_start,
            scheduled_end=request.scheduled_end,
            actual_start=request.actual_start,
            actual_end=request.actual_end,
            break_minutes=request.break_minutes,
            is_holiday=request.is_holiday,
            memo=request.memo,
        )

        # 응답 생성
        from app.repositories.employee_repo import EmployeeRepository
        emp_repo = EmployeeRepository(db)
        employee = await emp_repo.get_by_id(record.employee_id)

        response_data = {
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": employee.name if employee else "",
            "work_date": record.work_date,
            "scheduled_start": record.scheduled_start,
            "scheduled_end": record.scheduled_end,
            "actual_start": record.actual_start,
            "actual_end": record.actual_end,
            "break_minutes": record.break_minutes,
            "total_work_minutes": 0,  # 계산 필요
            "overtime_minutes": record.overtime_minutes,
            "night_minutes": record.night_minutes,
            "holiday_minutes": record.holiday_minutes,
            "is_holiday": record.is_holiday,
            "memo": record.memo,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

        return ApiResponse(data=response_data)

    except (NotFoundError, ConflictError) as e:
        raise e
    except Exception as e:
        raise ValidationError(message=str(e))


@router.get(
    "/records",
    response_model=ApiResponse[list[WorkRecordResponse]],
    summary="근무 기록 목록 조회",
    description="근무 기록 목록을 조회합니다."
)
async def list_work_records(
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    employee_id: UUID | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    year: int | None = None,
    month: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = None,
):
    """근무 기록 목록 조회"""
    from app.repositories.work_record_repo import WorkRecordRepository
    from app.repositories.employee_repo import EmployeeRepository

    # year/month 기반 날짜 범위 설정
    if year and month:
        import calendar
        from datetime import date as date_type
        from_date = date_type(year, month, 1)
        to_date = date_type(year, month, calendar.monthrange(year, month)[1])
    elif not from_date and not to_date:
        # 기본값: 현재월
        import calendar
        from datetime import date as date_type
        today = date_type.today()
        from_date = date_type(today.year, today.month, 1)
        to_date = date_type(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    repo = WorkRecordRepository(db)
    emp_repo = EmployeeRepository(db)

    records, next_cursor = await repo.list_by_company(
        company_id=UUID(company_id),
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        cursor=cursor,
    )

    # 응답 생성
    response_data = []
    for record in records:
        employee = await emp_repo.get_by_id(record.employee_id)
        response_data.append({
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": employee.name if employee else "",
            "work_date": record.work_date,
            "scheduled_start": record.scheduled_start,
            "scheduled_end": record.scheduled_end,
            "actual_start": record.actual_start,
            "actual_end": record.actual_end,
            "break_minutes": record.break_minutes,
            "total_work_minutes": 0,  # 계산 필요
            "overtime_minutes": record.overtime_minutes,
            "night_minutes": record.night_minutes,
            "holiday_minutes": record.holiday_minutes,
            "is_holiday": record.is_holiday,
            "memo": record.memo,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        })

    return ApiResponse(
        data=response_data,
        meta={
            "pagination": {
                "cursor": next_cursor,
                "hasNext": next_cursor is not None,
                "limit": limit,
            }
        }
    )


@router.get(
    "/records/{record_id}",
    response_model=ApiResponse[WorkRecordResponse],
    summary="근무 기록 상세 조회",
    description="근무 기록 상세 정보를 조회합니다."
)
async def get_work_record(
    record_id: UUID,
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """근무 기록 상세 조회"""
    from app.repositories.work_record_repo import WorkRecordRepository
    from app.repositories.employee_repo import EmployeeRepository

    repo = WorkRecordRepository(db)
    emp_repo = EmployeeRepository(db)

    record = await repo.get_by_id_and_company(record_id, UUID(company_id))
    if not record:
        raise NotFoundError("근무 기록을 찾을 수 없습니다.")

    employee = await emp_repo.get_by_id(record.employee_id)

    response_data = {
        "id": record.id,
        "employee_id": record.employee_id,
        "employee_name": employee.name if employee else "",
        "work_date": record.work_date,
        "scheduled_start": record.scheduled_start,
        "scheduled_end": record.scheduled_end,
        "actual_start": record.actual_start,
        "actual_end": record.actual_end,
        "break_minutes": record.break_minutes,
        "total_work_minutes": 0,  # 계산 필요
        "overtime_minutes": record.overtime_minutes,
        "night_minutes": record.night_minutes,
        "holiday_minutes": record.holiday_minutes,
        "is_holiday": record.is_holiday,
        "memo": record.memo,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }

    return ApiResponse(data=response_data)


@router.put(
    "/records/{record_id}",
    response_model=ApiResponse[WorkRecordResponse],
    summary="근무 기록 수정",
    description="근무 기록을 수정합니다."
)
async def update_work_record(
    record_id: UUID,
    request: WorkRecordUpdate,
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """근무 기록 수정"""
    service = AttendanceService(db)

    try:
        record = await service.update_record(
            company_id=UUID(company_id),
            record_id=record_id,
            work_date=request.work_date,
            scheduled_start=request.scheduled_start,
            scheduled_end=request.scheduled_end,
            actual_start=request.actual_start,
            actual_end=request.actual_end,
            break_minutes=request.break_minutes,
            is_holiday=request.is_holiday,
            memo=request.memo,
        )

        from app.repositories.employee_repo import EmployeeRepository
        emp_repo = EmployeeRepository(db)
        employee = await emp_repo.get_by_id(record.employee_id)

        response_data = {
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": employee.name if employee else "",
            "work_date": record.work_date,
            "scheduled_start": record.scheduled_start,
            "scheduled_end": record.scheduled_end,
            "actual_start": record.actual_start,
            "actual_end": record.actual_end,
            "break_minutes": record.break_minutes,
            "total_work_minutes": 0,  # 계산 필요
            "overtime_minutes": record.overtime_minutes,
            "night_minutes": record.night_minutes,
            "holiday_minutes": record.holiday_minutes,
            "is_holiday": record.is_holiday,
            "memo": record.memo,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

        return ApiResponse(data=response_data)

    except NotFoundError as e:
        raise e
    except Exception as e:
        raise ValidationError(message=str(e))


@router.delete(
    "/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="근무 기록 삭제",
    description="근무 기록을 삭제합니다."
)
async def delete_work_record(
    record_id: UUID,
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """근무 기록 삭제"""
    service = AttendanceService(db)

    try:
        await service.delete_record(UUID(company_id), record_id)
        return None
    except NotFoundError as e:
        raise e


@router.post(
    "/records/batch",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="근무 기록 일괄 생성",
    description="여러 근무 기록을 일괄 생성합니다."
)
async def batch_create_work_records(
    request: WorkRecordBatchCreate,
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """근무 기록 일괄 생성"""
    service = AttendanceService(db)

    total = len(request.records)
    created = 0
    skipped = 0
    errors = []

    for idx, record_data in enumerate(request.records):
        try:
            await service.create_record(
                company_id=UUID(company_id),
                employee_id=record_data.employee_id,
                work_date=record_data.work_date,
                scheduled_start=record_data.scheduled_start,
                scheduled_end=record_data.scheduled_end,
                actual_start=record_data.actual_start,
                actual_end=record_data.actual_end,
                break_minutes=record_data.break_minutes,
                is_holiday=record_data.is_holiday,
                memo=record_data.memo,
            )
            created += 1
        except (NotFoundError, ConflictError) as e:
            skipped += 1
            errors.append({
                "index": idx,
                "employee_id": str(record_data.employee_id),
                "work_date": str(record_data.work_date),
                "reason": str(e),
            })

    return ApiResponse(data={
        "total": total,
        "created": created,
        "skipped": skipped,
        "errors": errors,
    })


@router.post(
    "/import",
    response_model=ApiResponse[ImportResultResponse],
    summary="엑셀/CSV 임포트",
    description="엑셀 또는 CSV 파일을 업로드하여 근무 기록을 임포트합니다."
)
async def import_excel(
    file: UploadFile = File(...),
    req: Request = None,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """엑셀/CSV 임포트"""
    # 파일 크기 확인 (10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise ValidationError(
            message="파일 크기가 10MB를 초과합니다.",
            details=[{"field": "file", "message": "10MB 이하의 파일을 업로드하세요."}]
        )

    # 파일 다시 읽기
    await file.seek(0)

    service = ExcelImportService(db)

    try:
        # 1. 파일 파싱
        parsed_rows = await service.parse_file(file)

        # 2. 검증
        valid_rows, error_rows = await service.validate_rows(UUID(company_id), parsed_rows)

        # 3. 임포트
        result = await service.import_records(UUID(company_id), valid_rows)

        # 4. 에러 행 추가
        for error_row in error_rows:
            for error in error_row.errors:
                result['errors'].append({
                    "row": error_row.row_number,
                    "reason": error,
                })

        result['total_rows'] = len(parsed_rows)

        return ApiResponse(data=result)

    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError(message="임포트 중 오류 발생", details=[{"field": "file", "message": str(e)}])


@router.get(
    "/import/template",
    summary="엑셀 템플릿 다운로드",
    description="엑셀 업로드용 템플릿을 다운로드합니다."
)
async def download_template(
    req: Request,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """엑셀 템플릿 다운로드"""
    from fastapi.responses import StreamingResponse

    service = ExcelImportService(db)
    template = await service.generate_template(UUID(company_id))

    return StreamingResponse(
        iter([template.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=attendance_template.xlsx"}
    )


@router.get(
    "/summary",
    response_model=ApiResponse[MonthlySummaryResponse],
    summary="월별 근무 요약",
    description="월별 근무 기록 요약을 조회합니다."
)
async def get_monthly_summary(
    year: int = Query(..., ge=2020, le=2099),
    month: int = Query(..., ge=1, le=12),
    req: Request = None,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    employee_id: UUID | None = None,
):
    """월별 근무 요약 조회"""
    service = AttendanceService(db)

    try:
        result = await service.get_monthly_summary(
            company_id=UUID(company_id),
            year=year,
            month=month,
            employee_id=employee_id,
        )
        return ApiResponse(data=result)
    except Exception as e:
        raise ValidationError(message=str(e))


@router.get(
    "/analysis",
    response_model=ApiResponse[EmployeeAnalysisResponse],
    summary="직원 근무 패턴 분석",
    description="직원의 근무 패턴을 분석합니다."
)
async def get_employee_analysis(
    employee_id: UUID = Query(...),
    from_date: date | None = None,
    to_date: date | None = None,
    req: Request = None,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """직원 근무 패턴 분석"""
    service = AttendanceService(db)

    try:
        result = await service.get_employee_analysis(
            company_id=UUID(company_id),
            employee_id=employee_id,
            from_date=from_date,
            to_date=to_date,
        )
        return ApiResponse(data=result)
    except NotFoundError as e:
        raise e
    except Exception as e:
        raise ValidationError(message=str(e))
