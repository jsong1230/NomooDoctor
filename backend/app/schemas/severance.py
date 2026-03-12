# Severance 관련 스키마
from datetime import datetime, date
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field


class MonthlyWageInput(BaseModel):
    """월별 급여 입력"""
    year: int = Field(..., ge=2020, le=2099, description="연도")
    month: int = Field(..., ge=1, le=12, description="월")
    total_wage: Decimal = Field(..., gt=0, description="해당 월 총 급여")
    days_in_month: int = Field(..., ge=28, le=31, description="해당 월 총 일수")


class SeveranceCalculateRequest(BaseModel):
    """퇴직금 계산 요청"""
    employee_id: str = Field(..., description="직원 ID")
    resign_date: date = Field(..., description="퇴직 예정일")
    annual_bonus: Decimal = Field(default=Decimal("0"), ge=0, description="연간 상여금 총액")
    unused_annual_leave_days: int = Field(default=0, ge=0, le=40, description="미사용 연차 일수")
    monthly_wages: Optional[list[MonthlyWageInput]] = Field(
        default=None,
        description="최근 3개월 급여 (미입력 시 payslips에서 자동 조회)"
    )

    @classmethod
    def validate_monthly_wages(cls, v):
        if v is not None and len(v) != 3:
            raise ValueError("monthly_wages는 정확히 3개월 데이터여야 합니다.")
        return v


class CalculationDetail(BaseModel):
    """퇴직금 계산 상세 내역"""
    last_3_months_total_wage: int
    last_3_months_total_days: int
    bonus_3_months_share: int
    average_daily_wage: int
    severance_formula: str
    unused_leave_formula: str


class SeveranceCalculateResponse(BaseModel):
    """퇴직금 계산 결과"""
    employee_id: str
    employee_name: str
    hire_date: date
    resign_date: date
    total_service_days: int
    average_daily_wage: int
    severance_pay: int
    unused_leave_pay: int
    bonus_included: int
    total_payment: int
    payment_deadline: date
    eligible: bool
    calculation_detail: CalculationDetail


class SeveranceResponse(SeveranceCalculateResponse):
    """퇴직금 저장 결과"""
    id: str
    status: str
    created_at: datetime


class SeveranceSummary(BaseModel):
    """퇴직금 목록 요약"""
    id: str
    employee_id: str
    employee_name: str
    resign_date: date
    total_payment: int
    status: str
    payment_deadline: date
    created_at: datetime


class RiskFactors(BaseModel):
    """위험 요소 체크리스트"""
    is_pregnant: bool = False
    is_on_parental_leave: bool = False
    is_union_member: bool = False
    is_workplace_injury: bool = False
    is_whistleblower: bool = False


class TerminationGuideRequest(BaseModel):
    """해고 절차 가이드 요청"""
    employee_id: str = Field(..., description="직원 ID")
    termination_type: str = Field(
        ...,
        pattern="^(resignation|mutual_agreement|dismissal|contract_expiry|retirement)$",
        description="종료 유형"
    )
    reason: str = Field(..., max_length=500, description="퇴직 사유")
    risk_factors: RiskFactors = Field(default_factory=RiskFactors, description="위험 요소")


class ChecklistItem(BaseModel):
    """체크리스트 항목"""
    step: int
    title: str
    description: str
    required: bool
    completed: bool = False


class AdvanceNotice(BaseModel):
    """해고예고수당"""
    required: bool
    notice_days: int
    notice_pay_amount: int
    description: str


class RiskWarning(BaseModel):
    """위험 경고"""
    type: str
    severity: str
    message: str
    recommendation: str


class DocumentInfo(BaseModel):
    """서류 정보"""
    type: str
    name: str
    available: bool


class UnemploymentGuide(BaseModel):
    """실업급여 안내"""
    eligible: bool
    conditions: str
    required_documents: list[str]


class LawReference(BaseModel):
    """법 조항 인용"""
    law_name: str
    article: str
    content: str


class TerminationGuideResponse(BaseModel):
    """해고 절차 가이드 응답"""
    termination_type: str
    risk_level: str
    checklist: list[ChecklistItem]
    advance_notice: AdvanceNotice
    risk_warnings: list[RiskWarning]
    documents: list[DocumentInfo]
    unemployment_benefit_guide: UnemploymentGuide
    ai_guide: str
    law_references: list[LawReference]
    disclaimer: str


class DocumentGenerateRequest(BaseModel):
    """서류 생성 요청"""
    employee_id: str = Field(..., description="직원 ID")
    document_type: str = Field(
        ...,
        pattern="^(dismissal_notice|resignation_agreement)$",
        description="서류 유형"
    )
    termination_date: date = Field(..., description="해고/퇴직일")
    reason: str = Field(..., max_length=500, description="사유")
    format: str = Field(default="pdf", pattern="^(pdf|docx)$", description="파일 형식")


class DocumentGenerateResponse(BaseModel):
    """서류 생성 응답"""
    download_url: str
    expires_at: datetime
    filename: str
    document_type: str
