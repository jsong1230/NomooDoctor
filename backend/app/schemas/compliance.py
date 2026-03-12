# Compliance 관련 스키마
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class RiskDeduction(BaseModel):
    """리스크 감점 항목"""
    category: str = Field(..., description="위반 카테고리")
    deduction: int = Field(..., le=0, description="감점 점수 (음수)")
    count: int = Field(..., ge=0, description="위반 건수")
    message: str = Field(..., description="위반 설명 메시지")
    resolution: str = Field(..., description="해결 방법 안내")


class RiskScoreResponse(BaseModel):
    """리스크 스코어 응답"""
    score: int = Field(..., ge=0, le=100, description="리스크 스코어 (0~100)")
    level: Literal["green", "yellow", "red"] = Field(..., description="위험도 레벨")
    details: list[RiskDeduction] = Field(default_factory=list, description="감점 항목 목록")
    total_employees: int = Field(..., ge=0, description="활성 직원 수")
    employees_without_contract: int = Field(default=0, ge=0, description="계약서 미작성 직원 수")
    employees_without_payslip: int = Field(default=0, ge=0, description="급여명세서 미발송 직원 수")
    work_rule_required: bool = Field(default=False, description="취업규칙 작성 필요 여부")
    work_rule_exists: bool = Field(default=False, description="취업규칙 존재 여부")


class ComplianceEvent(BaseModel):
    """컴플라이언스 이벤트"""
    id: str = Field(..., description="이벤트 ID")
    event_type: Literal[
        "contract_expiry", "payroll_date", "work_rule_due", "insurance_report"
    ] = Field(..., description="이벤트 유형")
    title: str = Field(..., description="이벤트 제목")
    description: str = Field(default="", description="이벤트 설명")
    event_date: date = Field(..., description="이벤트 날짜")
    d_day: int | None = Field(None, description="D-Day (음수: 지남, 양수: 남은 일수)")
    severity: Literal["info", "warning", "critical"] = Field(
        default="info", description="심각도"
    )
    related_employee_id: str | None = Field(None, description="관련 직원 ID")
    related_employee_name: str | None = Field(None, description="관련 직원명")


class ComplianceEventsResponse(BaseModel):
    """컴플라이언스 이벤트 목록 응답"""
    events: list[ComplianceEvent] = Field(default_factory=list, description="이벤트 목록")
    year: int = Field(..., description="조회 연도")
    month: int = Field(..., description="조회 월")


class UpcomingEventsResponse(BaseModel):
    """향후 이벤트 목록 응답"""
    events: list[ComplianceEvent] = Field(default_factory=list, description="이벤트 목록")
    period_days: int = Field(..., description="조회 기간 (일)")


class MonthlyRiskScore(BaseModel):
    """월별 리스크 스코어"""
    year: int
    month: int
    score: int = Field(..., ge=0, le=100)
    level: Literal["green", "yellow", "red"]


class RiskScoreHistoryResponse(BaseModel):
    """리스크 스코어 히스토리 응답"""
    history: list[MonthlyRiskScore] = Field(default_factory=list, description="월별 리스크 스코어 목록")
