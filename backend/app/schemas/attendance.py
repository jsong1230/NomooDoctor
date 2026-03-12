# 근태 관리 스키마
from datetime import date, time, datetime
from uuid import UUID
from pydantic import BaseModel, Field


# === Request Schemas ===

class WorkRecordCreate(BaseModel):
    """근무 기록 생성 요청"""
    employee_id: UUID
    work_date: date
    scheduled_start: time
    scheduled_end: time
    actual_start: time | None = None
    actual_end: time | None = None
    break_minutes: int = Field(default=60, ge=0, le=480)
    is_holiday: bool = False
    memo: str | None = Field(default=None, max_length=500)


class WorkRecordUpdate(BaseModel):
    """근무 기록 수정 요청"""
    work_date: date | None = None
    scheduled_start: time | None = None
    scheduled_end: time | None = None
    actual_start: time | None = None
    actual_end: time | None = None
    break_minutes: int | None = Field(default=None, ge=0, le=480)
    is_holiday: bool | None = None
    memo: str | None = Field(default=None, max_length=500)


class WorkRecordBatchCreate(BaseModel):
    """근무 기록 일괄 생성 요청"""
    records: list[WorkRecordCreate] = Field(..., min_length=1, max_length=500)


# === Response Schemas ===

class WorkRecordResponse(BaseModel):
    """근무 기록 응답"""
    id: UUID
    employee_id: UUID
    employee_name: str
    work_date: date
    scheduled_start: time
    scheduled_end: time
    actual_start: time | None
    actual_end: time | None
    break_minutes: int
    total_work_minutes: int  # 계산 필드
    overtime_minutes: int
    night_minutes: int
    holiday_minutes: int
    is_holiday: bool
    memo: str | None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ImportErrorDetail(BaseModel):
    """엑셀 import 오류 상세"""
    row: int
    column: str | None = None
    value: str | None = None
    reason: str


class ImportResultResponse(BaseModel):
    """엑셀 import 결과"""
    total_rows: int
    created: int
    updated: int
    skipped: int
    errors: list[ImportErrorDetail]


class EmployeeMonthlySummary(BaseModel):
    """직원별 월 요약"""
    employee_id: UUID
    employee_name: str
    employment_type: str
    total_work_days: int
    total_work_minutes: int
    total_overtime_minutes: int
    total_night_minutes: int
    total_holiday_minutes: int
    total_break_minutes: int
    late_count: int
    early_leave_count: int
    absent_count: int


class CompanyTotalSummary(BaseModel):
    """사업장 전체 월 요약"""
    total_employees: int
    avg_work_minutes_per_day: int
    total_overtime_minutes: int
    total_night_minutes: int
    total_holiday_minutes: int


class MonthlySummaryResponse(BaseModel):
    """월별 요약 응답"""
    year: int
    month: int
    employees: list[EmployeeMonthlySummary]
    company_total: CompanyTotalSummary


class OvertimeTrend(BaseModel):
    """연장근무 추세"""
    year: int
    month: int
    total_minutes: int


class PatternData(BaseModel):
    """패턴 분석 데이터"""
    avg_start_time: str  # "HH:MM"
    avg_end_time: str
    avg_work_minutes_per_day: int
    avg_overtime_minutes_per_month: int
    overtime_trend: list[OvertimeTrend]
    weekday_distribution: dict[str, int]  # {"mon": 95, ...}
    weekly_hours_warning: bool


class AnalysisAlert(BaseModel):
    """분석 경고"""
    type: str  # "overtime_high", "night_frequent", "weekly_52h_exceeded"
    message: str


class EmployeeAnalysisResponse(BaseModel):
    """직원 분석 응답"""
    employee_id: UUID
    employee_name: str
    period: dict[str, str]  # {"from": "...", "to": "..."}
    pattern: PatternData
    alerts: list[AnalysisAlert]
