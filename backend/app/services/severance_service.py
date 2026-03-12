# 퇴직금/해고 계산 서비스
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from app.db.models.employee import Employee
from app.db.models.salary import Payslip
from app.db.models.company import Company
from app.schemas.severance import (
    SeveranceCalculateRequest,
    SeveranceCalculateResponse,
    SeveranceResponse,
    MonthlyWageInput,
    TerminationGuideRequest,
    TerminationGuideResponse,
    RiskFactors,
    ChecklistItem,
    AdvanceNotice,
    RiskWarning,
    DocumentInfo,
    UnemploymentGuide,
    LawReference,
    CalculationDetail,
)
from app.repositories.severance_repo import SeveranceRepository
from app.repositories.termination_doc_repo import TerminationDocRepository
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.company_repo import CompanyRepository
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
)
from sqlalchemy import select


# 상수
SEVERANCE_DAYS = Decimal("30")
SEVERANCE_YEAR_DAYS = Decimal("365")
BONUS_MONTHS_RATIO = Decimal("3") / Decimal("12")
PAYMENT_DEADLINE_DAYS = 14
MIN_SERVICE_DAYS = 365


class SeveranceService:
    """퇴직금/해고 계산 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.severance_repo = SeveranceRepository(db)
        self.termination_doc_repo = TerminationDocRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.company_repo = CompanyRepository(db)

    @staticmethod
    def truncate_to_10_won(value: Decimal) -> int:
        """10원 미만 절사"""
        value_int = int(value)
        return (value_int // 10) * 10

    @staticmethod
    def compute_total_service_days(hire_date: date, resign_date: date) -> int:
        """총 재직일수 계산"""
        delta = resign_date - hire_date
        return delta.days

    @staticmethod
    def compute_average_daily_wage(
        monthly_wages: list[MonthlyWageInput],
        annual_bonus: Decimal,
    ) -> tuple[Decimal, dict]:
        """평균임금 계산

        평균임금 = (최근 3개월 임금 합계 + 상여금 3/12) / 최근 3개월 총 일수
        """
        total_wage = sum(Decimal(str(w.total_wage)) for w in monthly_wages)
        total_days = sum(w.days_in_month for w in monthly_wages)
        bonus_3m = annual_bonus * BONUS_MONTHS_RATIO

        average_daily_wage = (total_wage + bonus_3m) / Decimal(str(total_days))

        return average_daily_wage, {
            "last_3_months_total_wage": int(total_wage),
            "last_3_months_total_days": total_days,
            "bonus_3_months_share": int(bonus_3m),
            "average_daily_wage": int(average_daily_wage),
        }

    @staticmethod
    def compute_severance_pay(
        average_daily_wage: Decimal,
        total_service_days: int,
    ) -> int:
        """퇴직금 계산

        퇴직금 = 평균임금 x 30일 x (총 재직일수 / 365)
        10원 미만 절사
        """
        severance = (
            average_daily_wage
            * SEVERANCE_DAYS
            * (Decimal(str(total_service_days)) / SEVERANCE_YEAR_DAYS)
        )
        return SeveranceService.truncate_to_10_won(severance)

    @staticmethod
    def compute_unused_leave_pay(
        average_daily_wage: Decimal,
        unused_days: int,
    ) -> int:
        """연차 미사용 수당 계산

        미사용 수당 = 평균임금 x 미사용 연차일수
        10원 미만 절사
        """
        if unused_days == 0:
            return 0

        unused_pay = average_daily_wage * Decimal(str(unused_days))
        return SeveranceService.truncate_to_10_won(unused_pay)

    @staticmethod
    def compute_payment_deadline(resign_date: date) -> date:
        """지급 기한 계산 (퇴직일 + 14일)"""
        return resign_date + timedelta(days=PAYMENT_DEADLINE_DAYS)

    async def _get_recent_payslips(
        self,
        employee_id: UUID,
        resign_date: date,
        months: int = 3,
    ) -> list[MonthlyWageInput] | None:
        """최근 N개월 급여 데이터 조회 (payslips 테이블)"""
        # resign_date 기준으로 최근 3개월 조회
        target_year = resign_date.year
        target_month = resign_date.month

        payslips_data = []
        for _ in range(months):
            result = await self.db.execute(
                select(Payslip).where(
                    and_(
                        Payslip.employee_id == employee_id,
                        Payslip.pay_year == target_year,
                        Payslip.pay_month == target_month,
                    )
                )
            )
            payslip = result.scalar_one_or_none()
            if not payslip:
                return None

            # 급여 = 기본급 + 모든 수당
            total_wage = Decimal(str(payslip.gross_pay))

            # 해당 월 일수 계산
            if target_month == 2:
                days_in_month = 29 if (target_year % 4 == 0 and target_year % 100 != 0) or (target_year % 400 == 0) else 28
            elif target_month in [4, 6, 9, 11]:
                days_in_month = 30
            else:
                days_in_month = 31

            payslips_data.append(
                MonthlyWageInput(
                    year=target_year,
                    month=target_month,
                    total_wage=total_wage,
                    days_in_month=days_in_month,
                )
            )

            # 이전 달로 이동
            target_month -= 1
            if target_month == 0:
                target_month = 12
                target_year -= 1

        # 역순으로 정렬 (가장 오래된 월부터)
        return list(reversed(payslips_data))

    async def calculate_severance(
        self,
        db: AsyncSession,
        company_id: UUID,
        request: SeveranceCalculateRequest,
    ) -> SeveranceCalculateResponse:
        """퇴직금 시뮬레이션 (DB 저장 없음)"""
        # 직원 조회
        employee = await self.employee_repo.get_by_id_and_company(
            UUID(request.employee_id), company_id
        )
        if not employee:
            from app.core.exceptions import EmployeeNotFoundError
            raise EmployeeNotFoundError()

        # 퇴사일 검증
        if request.resign_date <= employee.hire_date:
            from app.core.exceptions import InvalidResignDateError
            raise InvalidResignDateError()

        # 재직일수 계산
        total_service_days = self.compute_total_service_days(
            employee.hire_date, request.resign_date
        )

        # 1년 미만 검증
        if total_service_days < MIN_SERVICE_DAYS:
            from app.core.exceptions import MinimumServiceDaysError
            raise MinimumServiceDaysError()

        # 월별 급여 데이터 처리
        if request.monthly_wages:
            monthly_wages = request.monthly_wages
        else:
            # payslips에서 자동 조회
            monthly_wages = await self._get_recent_payslips(
                UUID(request.employee_id), request.resign_date
            )
            if not monthly_wages:
                from app.core.exceptions import InsufficientWageDataError
                raise InsufficientWageDataError()

        # 평균임금 계산
        average_daily_wage, calc_detail = self.compute_average_daily_wage(
            monthly_wages, request.annual_bonus
        )

        # 퇴직금 계산
        severance_pay = self.compute_severance_pay(average_daily_wage, total_service_days)

        # 연차 미사용 수당
        unused_leave_pay = self.compute_unused_leave_pay(
            average_daily_wage, request.unused_annual_leave_days
        )

        # 상여금 포함액
        bonus_included = int(
            request.annual_bonus * BONUS_MONTHS_RATIO
            if request.annual_bonus > 0
            else 0
        )

        # 지급 기한
        payment_deadline = self.compute_payment_deadline(request.resign_date)

        # 총 지급액
        total_payment = severance_pay + unused_leave_pay

        # 계산 상세 내역
        calculation_detail = CalculationDetail(
            last_3_months_total_wage=calc_detail["last_3_months_total_wage"],
            last_3_months_total_days=calc_detail["last_3_months_total_days"],
            bonus_3_months_share=calc_detail["bonus_3_months_share"],
            average_daily_wage=int(average_daily_wage),
            severance_formula=f"{int(average_daily_wage)} * 30 * ({total_service_days} / 365)",
            unused_leave_formula=f"{int(average_daily_wage)} * {request.unused_annual_leave_days}",
        )

        return SeveranceCalculateResponse(
            employee_id=str(employee.id),
            employee_name=employee.name,
            hire_date=employee.hire_date,
            resign_date=request.resign_date,
            total_service_days=total_service_days,
            average_daily_wage=int(average_daily_wage),
            severance_pay=severance_pay,
            unused_leave_pay=unused_leave_pay,
            bonus_included=bonus_included,
            total_payment=total_payment,
            payment_deadline=payment_deadline,
            eligible=True,
            calculation_detail=calculation_detail,
        )

    async def create_severance(
        self,
        db: AsyncSession,
        company_id: UUID,
        request: SeveranceCalculateRequest,
    ) -> SeveranceResponse:
        """퇴직금 확정 저장"""
        # 중복 체크
        existing = await self.severance_repo.get_by_employee_and_date(
            UUID(request.employee_id), request.resign_date
        )
        if existing:
            from app.core.exceptions import DuplicateSeveranceError
            raise DuplicateSeveranceError()

        # 계산 수행
        calc_result = await self.calculate_severance(db, company_id, request)

        # DB에 저장
        record = await self.severance_repo.create(
            {
                "employee_id": UUID(request.employee_id),
                "company_id": company_id,
                "hire_date": calc_result.hire_date,
                "resign_date": calc_result.resign_date,
                "total_service_days": calc_result.total_service_days,
                "last_3m_total_wage": calc_result.calculation_detail.last_3_months_total_wage,
                "last_3m_total_days": calc_result.calculation_detail.last_3_months_total_days,
                "bonus_3m_share": calc_result.calculation_detail.bonus_3_months_share,
                "average_daily_wage": calc_result.average_daily_wage,
                "severance_pay": calc_result.severance_pay,
                "unused_leave_days": request.unused_annual_leave_days,
                "unused_leave_pay": calc_result.unused_leave_pay,
                "total_payment": calc_result.total_payment,
                "payment_deadline": calc_result.payment_deadline,
                "status": "calculated",
                "calculation_detail": calc_result.calculation_detail.model_dump(),
            }
        )

        await self.db.commit()

        return SeveranceResponse(
            id=str(record.id),
            employee_id=str(record.employee_id),
            employee_name=calc_result.employee_name,
            hire_date=record.hire_date,
            resign_date=record.resign_date,
            total_service_days=record.total_service_days,
            average_daily_wage=int(record.average_daily_wage),
            severance_pay=int(record.severance_pay),
            unused_leave_pay=int(record.unused_leave_pay),
            bonus_included=calc_result.bonus_included,
            total_payment=int(record.total_payment),
            payment_deadline=record.payment_deadline,
            eligible=True,
            calculation_detail=calc_result.calculation_detail,
            status=record.status,
            created_at=record.created_at,
        )

    def _detect_risk_level(self, termination_type: str, risk_factors: RiskFactors) -> str:
        """위험도 판정

        - EMERGENCY: 임신, 육아휴직, 산재 중
        - HIGH: 노조활동, 내부고발자
        - MEDIUM: 해고 유형
        - LOW: 자발적 퇴사, 계약만료, 정년퇴직
        """
        RISK_LEVEL_MAP = {
            "is_pregnant": "EMERGENCY",
            "is_on_parental_leave": "EMERGENCY",
            "is_workplace_injury": "EMERGENCY",
            "is_union_member": "HIGH",
            "is_whistleblower": "HIGH",
        }

        priority = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "EMERGENCY": 3}
        max_level = "LOW"

        # 종료 유형에 따른 기본 위험도
        if termination_type == "dismissal":
            max_level = "MEDIUM"

        # 위험 요소별 위험도 상향
        for factor, level in RISK_LEVEL_MAP.items():
            if getattr(risk_factors, factor, False):
                if priority[level] > priority[max_level]:
                    max_level = level

        return max_level

    def _build_checklist(
        self, termination_type: str, risk_level: str
    ) -> list[ChecklistItem]:
        """종료 유형별 정적 체크리스트 구성"""
        checklist = []

        if termination_type == "dismissal":
            checklist.extend(
                [
                    ChecklistItem(
                        step=1,
                        title="해고 사유 정당성 확인",
                        description="근로기준법 제23조에 따라 정당한 사유가 있는지 확인",
                        required=True,
                    ),
                    ChecklistItem(
                        step=2,
                        title="서면 통지",
                        description="근로기준법 제27조에 따라 해고사유를 서면으로 통지",
                        required=True,
                    ),
                    ChecklistItem(
                        step=3,
                        title="해고 예고",
                        description="30일 전 예고 또는 30일분 통상임금 지급",
                        required=True,
                    ),
                    ChecklistItem(
                        step=4,
                        title="인증서 준비",
                        description="해고예고통지서, 인수인계 기록 등 증거 자료 준비",
                        required=True,
                    ),
                    ChecklistItem(
                        step=5,
                        title="퇴직금 계산 및 지급",
                        description="재직 1년 이상 시 퇴직금 지급 (14일 이내)",
                        required=True,
                    ),
                ]
            )
        elif termination_type == "mutual_agreement":
            checklist.extend(
                [
                    ChecklistItem(
                        step=1,
                        title="합의서 작성",
                        description="권고사직 합의서를 작성하고 양측 서명",
                        required=True,
                    ),
                    ChecklistItem(
                        step=2,
                        title="퇴직금 협의",
                        description="퇴직금 산정 및 지급 일정 합의",
                        required=True,
                    ),
                    ChecklistItem(
                        step=3,
                        title="실업급여 안내",
                        description="고용센터 실업급여 신청 안내",
                        required=True,
                    ),
                ]
            )
        elif termination_type == "resignation":
            checklist.extend(
                [
                    ChecklistItem(
                        step=1,
                        title="퇴직원 접수",
                        description="직원의 퇴직 의사 확인 및 기록",
                        required=True,
                    ),
                    ChecklistItem(
                        step=2,
                        title="최종 급여 산정",
                        description="퇴직금 및 미지급 급여 계산",
                        required=True,
                    ),
                    ChecklistItem(
                        step=3,
                        title="퇴직금 지급",
                        description="재직 1년 이상 시 퇴직금 지급 (14일 이내)",
                        required=True,
                    ),
                ]
            )
        elif termination_type == "contract_expiry":
            checklist.extend(
                [
                    ChecklistItem(
                        step=1,
                        title="계약 만료 확인",
                        description="근로계약서의 계약 만료일 확인",
                        required=True,
                    ),
                    ChecklistItem(
                        step=2,
                        title="갱신 여부 결정",
                        description="재계약 여부 30일 전에 통보",
                        required=True,
                    ),
                    ChecklistItem(
                        step=3,
                        title="퇴직금 지급",
                        description="재직 1년 이상 시 퇴직금 지급",
                        required=True,
                    ),
                ]
            )
        elif termination_type == "retirement":
            checklist.extend(
                [
                    ChecklistItem(
                        step=1,
                        title="정년 확인",
                        description="취업규칙에 정한 정년에 도달했는지 확인",
                        required=True,
                    ),
                    ChecklistItem(
                        step=2,
                        title="퇴직금 계산",
                        description="퇴직금 정확히 계산 (1년 이상)",
                        required=True,
                    ),
                    ChecklistItem(
                        step=3,
                        title="퇴직금 지급",
                        description="퇴직금 지급 (14일 이내)",
                        required=True,
                    ),
                ]
            )

        return checklist

    def _calculate_advance_notice_pay(
        self, termination_type: str, monthly_wage: int = 3000000
    ) -> AdvanceNotice:
        """해고예고수당 계산"""
        if termination_type == "dismissal":
            return AdvanceNotice(
                required=True,
                notice_days=30,
                notice_pay_amount=monthly_wage,
                description="30일 전 서면 예고 또는 30일분 통상임금 지급",
            )
        else:
            return AdvanceNotice(
                required=False,
                notice_days=0,
                notice_pay_amount=0,
                description="해고가 아닌 경우 해고예고수당 불필요",
            )

    async def generate_termination_guide(
        self,
        db: AsyncSession,
        company_id: UUID,
        request: TerminationGuideRequest,
    ) -> TerminationGuideResponse:
        """해고/퇴직 절차 가이드 생성"""
        # 직원 조회
        employee = await self.employee_repo.get_by_id_and_company(
            UUID(request.employee_id), company_id
        )
        if not employee:
            from app.core.exceptions import EmployeeNotFoundError
            raise EmployeeNotFoundError()

        # 회사 조회
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise NotFoundError(message="사업장을 찾을 수 없습니다.")

        # 위험도 판정
        risk_level = self._detect_risk_level(request.termination_type, request.risk_factors)

        # 체크리스트 구성
        checklist = self._build_checklist(request.termination_type, risk_level)

        # 해고예고수당 계산
        advance_notice = self._calculate_advance_notice_pay(request.termination_type)

        # 위험 경고 구성
        risk_warnings = []
        if request.risk_factors.is_pregnant:
            risk_warnings.append(
                RiskWarning(
                    type="pregnancy",
                    severity="EMERGENCY",
                    message="임산부 해고는 근로기준법 제65조에 의해 금지됩니다.",
                    recommendation="노무사 상담을 강력히 권장합니다.",
                )
            )
        if request.risk_factors.is_on_parental_leave:
            risk_warnings.append(
                RiskWarning(
                    type="parental_leave",
                    severity="EMERGENCY",
                    message="육아휴직 중인 직원 해고는 고용보험법에 의해 금지됩니다.",
                    recommendation="노무사 상담을 강력히 권장합니다.",
                )
            )
        if request.risk_factors.is_workplace_injury:
            risk_warnings.append(
                RiskWarning(
                    type="workplace_injury",
                    severity="EMERGENCY",
                    message="산업재해 요양 중인 직원 해고는 산업재해보상보험법으로 금지됩니다.",
                    recommendation="노무사 상담을 강력히 권장합니다.",
                )
            )
        if request.risk_factors.is_union_member:
            risk_warnings.append(
                RiskWarning(
                    type="union_member",
                    severity="HIGH",
                    message="노조활동을 이유로 한 해고는 부당해고로 판단될 가능성이 높습니다.",
                    recommendation="노무사와 상담 후 진행하세요.",
                )
            )
        if request.risk_factors.is_whistleblower:
            risk_warnings.append(
                RiskWarning(
                    type="whistleblower",
                    severity="HIGH",
                    message="내부고발자 해고는 법적 보호 대상입니다.",
                    recommendation="법무팀 또는 노무사와 상담 후 진행하세요.",
                )
            )

        # 서류 정보
        documents = [
            DocumentInfo(type="dismissal_notice", name="해고예고통지서", available=True),
            DocumentInfo(type="resignation_agreement", name="권고사직서", available=True),
        ]

        # 실업급여 안내
        if request.termination_type in ["dismissal", "mutual_agreement"]:
            unemployment_guide = UnemploymentGuide(
                eligible=True,
                conditions="비자발적 이직(해고/권고사직) 시 실업급여 수급 가능",
                required_documents=["이직확인서", "구직신청서", "신분증"],
            )
        else:
            unemployment_guide = UnemploymentGuide(
                eligible=False,
                conditions="자발적 퇴사(사직)는 실업급여 수급이 제한됩니다.",
                required_documents=[],
            )

        # 법 조항 인용
        law_references = [
            LawReference(
                law_name="근로기준법",
                article="제23조",
                content="해고는 정당한 사유 없이 하지 못합니다.",
            ),
            LawReference(
                law_name="근로기준법",
                article="제26조",
                content="사용자가 근로자를 해고하고자 할 때에는 적어도 30일 전에 예고하거나 30일 이상의 통상임금을 지급해야 합니다.",
            ),
        ]

        # AI 가이드 생성 (모의 구현)
        ai_guide = f"""해고/퇴직 유형: {request.termination_type}

법적 검토:
근로기준법 제23조에 따르면 해고는 정당한 사유가 있어야 합니다. {request.reason}이(가) 정당한 사유에 해당하는지 검토가 필요합니다.

절차:
1. 해고 사유의 정당성 재확인
2. 관련 증거 자료 수집
3. 법적 자문 취득
4. 서면 통지 및 예고
5. 퇴직금 산정 및 지급

주의사항:
{request.termination_type}의 경우, 근로기준법 및 판례에 따른 법적 위험을 신중하게 검토하세요.
특히 노조활동, 임신, 육아휴직 등의 사유로 인한 해고는 엄격히 규제됩니다."""

        # 면책 문구
        disclaimer = (
            "본 가이드는 참고용이며, 법적 효력이 없습니다. "
            "구체적 사안에 대해서는 전문 노무사와 상담하시기 바랍니다."
        )

        return TerminationGuideResponse(
            termination_type=request.termination_type,
            risk_level=risk_level,
            checklist=checklist,
            advance_notice=advance_notice,
            risk_warnings=risk_warnings,
            documents=documents,
            unemployment_benefit_guide=unemployment_guide,
            ai_guide=ai_guide,
            law_references=law_references,
            disclaimer=disclaimer,
        )
