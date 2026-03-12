# Compliance 서비스 — 컴플라이언스 대시보드 비즈니스 로직
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
import uuid
import logging

from app.db.models import Company, Employee, Contract, Payslip, WorkRule
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

# 감점 기준
DEDUCTION_NO_CONTRACT = -10    # 근로계약서 미작성 1인당
DEDUCTION_NO_WORK_RULE = -20  # 취업규칙 미작성 (10인 이상)
DEDUCTION_NO_PAYSLIP = -5     # 급여명세서 미발송 1인당

# 스코어 레벨 기준
LEVEL_GREEN_MIN = 80   # 80~100 초록
LEVEL_YELLOW_MIN = 60  # 60~79 노랑
# 0~59 빨강


def _get_score_level(score: int) -> str:
    """점수에 따른 레벨 반환"""
    if score >= LEVEL_GREEN_MIN:
        return "green"
    elif score >= LEVEL_YELLOW_MIN:
        return "yellow"
    return "red"


class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_company(self, company_id: uuid.UUID) -> Company:
        """회사 조회 (없으면 NotFoundError)"""
        result = await self.db.execute(
            select(Company).where(
                and_(Company.id == company_id, Company.is_deleted == False)
            )
        )
        company = result.scalar_one_or_none()
        if not company:
            raise NotFoundError(message="사업장을 찾을 수 없습니다.")
        return company

    async def _get_active_employees(self, company_id: uuid.UUID) -> list[Employee]:
        """활성 직원 목록 조회"""
        result = await self.db.execute(
            select(Employee)
            .where(
                and_(
                    Employee.company_id == company_id,
                    Employee.is_active == True,
                )
            )
            .order_by(Employee.name)
        )
        return list(result.scalars().all())

    async def _get_signed_contracts_employee_ids(
        self, company_id: uuid.UUID
    ) -> set[uuid.UUID]:
        """서명 완료된 유효 계약서가 있는 직원 ID 집합 반환"""
        today = date.today()
        result = await self.db.execute(
            select(Contract.employee_id).where(
                and_(
                    Contract.company_id == company_id,
                    Contract.status.in_(["signed", "sent"]),
                    or_(
                        Contract.end_date == None,
                        Contract.end_date >= today,
                    ),
                )
            ).distinct()
        )
        return set(result.scalars().all())

    async def _get_current_month_payslip_employee_ids(
        self, company_id: uuid.UUID
    ) -> set[uuid.UUID]:
        """현재 월 급여명세서 발송된 직원 ID 집합 반환"""
        today = date.today()
        result = await self.db.execute(
            select(Payslip.employee_id).where(
                and_(
                    Payslip.company_id == company_id,
                    Payslip.pay_year == today.year,
                    Payslip.pay_month == today.month,
                    Payslip.send_status == "sent",
                )
            ).distinct()
        )
        return set(result.scalars().all())

    async def _has_active_work_rule(self, company_id: uuid.UUID) -> bool:
        """활성 취업규칙 존재 여부"""
        result = await self.db.execute(
            select(func.count(WorkRule.id)).where(
                and_(
                    WorkRule.company_id == company_id,
                    WorkRule.status == "active",
                )
            )
        )
        count = result.scalar_one()
        return count > 0

    async def calculate_risk_score(self, company_id: uuid.UUID) -> dict:
        """
        리스크 스코어 계산
        기본 100점에서 감점 방식

        Returns: {
            "score": 85,
            "level": "green",
            "details": [...],
            "total_employees": 10,
            "employees_without_contract": 1,
            "employees_without_payslip": 1,
            "work_rule_required": True,
            "work_rule_exists": True,
        }
        """
        company = await self._get_company(company_id)
        active_employees = await self._get_active_employees(company_id)
        total_employees = len(active_employees)

        if total_employees == 0:
            return {
                "score": 100,
                "level": "green",
                "details": [],
                "total_employees": 0,
                "employees_without_contract": 0,
                "employees_without_payslip": 0,
                "work_rule_required": company.work_rule_required,
                "work_rule_exists": False,
            }

        employee_ids = {e.id for e in active_employees}
        employee_name_map = {e.id: e.name for e in active_employees}

        # 1) 근로계약서 체크
        contracted_ids = await self._get_signed_contracts_employee_ids(company_id)
        without_contract_ids = employee_ids - contracted_ids
        without_contract_count = len(without_contract_ids)

        # 2) 급여명세서 체크 (현재 월)
        payslip_sent_ids = await self._get_current_month_payslip_employee_ids(company_id)
        without_payslip_ids = employee_ids - payslip_sent_ids
        without_payslip_count = len(without_payslip_ids)

        # 3) 취업규칙 체크
        work_rule_required = company.work_rule_required  # employee_count >= 10
        work_rule_exists = await self._has_active_work_rule(company_id)

        # 감점 계산
        score = 100
        details: list[dict] = []

        # 근로계약서 감점
        if without_contract_count > 0:
            deduction = DEDUCTION_NO_CONTRACT * without_contract_count
            names = ", ".join(
                employee_name_map[eid]
                for eid in sorted(without_contract_ids, key=lambda x: employee_name_map[x])
            )
            details.append({
                "category": "근로계약서",
                "deduction": deduction,
                "count": without_contract_count,
                "message": f"근로계약서 미작성 직원 {without_contract_count}명 ({names})",
                "resolution": "직원 관리 > 계약서 작성에서 근로계약서를 생성하고 서명을 받으세요. "
                              "근로기준법 제17조에 따라 서면 근로조건 명시가 의무입니다.",
            })
            score += deduction

        # 취업규칙 감점
        if work_rule_required and not work_rule_exists:
            details.append({
                "category": "취업규칙",
                "deduction": DEDUCTION_NO_WORK_RULE,
                "count": 1,
                "message": "10인 이상 사업장이나 취업규칙이 작성되지 않았습니다.",
                "resolution": "취업규칙 관리에서 취업규칙을 작성하고 근로자 과반수 의견을 들어 신고하세요. "
                              "근로기준법 제93조에 따라 10인 이상 사업장은 취업규칙 작성 및 신고가 의무입니다.",
            })
            score += DEDUCTION_NO_WORK_RULE

        # 급여명세서 감점
        if without_payslip_count > 0:
            deduction = DEDUCTION_NO_PAYSLIP * without_payslip_count
            names = ", ".join(
                employee_name_map[eid]
                for eid in sorted(without_payslip_ids, key=lambda x: employee_name_map[x])
            )
            details.append({
                "category": "급여명세서",
                "deduction": deduction,
                "count": without_payslip_count,
                "message": f"급여명세서 미발송 {without_payslip_count}건 ({names})",
                "resolution": "급여 관리 > 급여명세서에서 해당 직원의 급여명세서를 생성하고 발송하세요. "
                              "근로기준법 제48조에 따라 임금명세서 교부가 의무입니다.",
            })
            score += deduction

        # 최소 0점
        score = max(score, 0)

        return {
            "score": score,
            "level": _get_score_level(score),
            "details": details,
            "total_employees": total_employees,
            "employees_without_contract": without_contract_count,
            "employees_without_payslip": without_payslip_count,
            "work_rule_required": work_rule_required,
            "work_rule_exists": work_rule_exists,
        }

    async def get_compliance_events(
        self, company_id: uuid.UUID, year: int, month: int
    ) -> list[dict]:
        """
        노무 이벤트 목록 (캘린더용)
        - 계약 만료일 (contracts 테이블에서 end_date 조회)
        - 급여 지급일 (매월 25일 기본)
        """
        company = await self._get_company(company_id)
        events: list[dict] = []
        today = date.today()

        # 해당 월의 첫날/마지막날
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        # 1) 계약 만료 이벤트
        result = await self.db.execute(
            select(Contract)
            .options(selectinload(Contract.employee))
            .where(
                and_(
                    Contract.company_id == company_id,
                    Contract.end_date != None,
                    Contract.end_date >= first_day,
                    Contract.end_date <= last_day,
                    Contract.status.in_(["signed", "sent"]),
                )
            )
            .order_by(Contract.end_date)
        )
        contracts = list(result.scalars().all())

        for contract in contracts:
            d_day = (contract.end_date - today).days
            employee_name = contract.employee.name if contract.employee else "알 수 없음"

            severity = "info"
            if 0 <= d_day <= 7:
                severity = "critical"
            elif 0 <= d_day <= 30:
                severity = "warning"

            events.append({
                "id": f"contract_expiry_{contract.id}",
                "event_type": "contract_expiry",
                "title": f"{employee_name} 계약 만료",
                "description": f"{employee_name}님의 근로계약이 {contract.end_date.strftime('%Y-%m-%d')}에 만료됩니다.",
                "event_date": contract.end_date.isoformat(),
                "d_day": d_day,
                "severity": severity,
                "related_employee_id": str(contract.employee_id),
                "related_employee_name": employee_name,
            })

        # 2) 급여 지급일 이벤트 (매월 25일)
        payroll_day = 25
        # 25일이 해당 월 범위 안에 있는지 확인
        if payroll_day <= last_day.day:
            payroll_date = date(year, month, payroll_day)
            d_day = (payroll_date - today).days
            severity = "info"
            if 0 <= d_day <= 3:
                severity = "warning"
            elif d_day < 0:
                severity = "info"

            events.append({
                "id": f"payroll_date_{year}_{month:02d}",
                "event_type": "payroll_date",
                "title": f"{month}월 급여 지급일",
                "description": f"{year}년 {month}월 급여 지급일입니다.",
                "event_date": payroll_date.isoformat(),
                "d_day": d_day,
                "severity": severity,
                "related_employee_id": None,
                "related_employee_name": None,
            })

        # 날짜순 정렬
        events.sort(key=lambda e: e["event_date"])
        return events

    async def get_upcoming_events(
        self, company_id: uuid.UUID, days: int = 30
    ) -> list[dict]:
        """
        향후 이벤트 (D-30, D-7 등)
        - 계약 만료 임박
        - 급여 지급일 리마인더
        """
        company = await self._get_company(company_id)
        events: list[dict] = []
        today = date.today()
        end_date_limit = today + timedelta(days=days)

        # 1) 계약 만료 임박
        result = await self.db.execute(
            select(Contract)
            .options(selectinload(Contract.employee))
            .where(
                and_(
                    Contract.company_id == company_id,
                    Contract.end_date != None,
                    Contract.end_date >= today,
                    Contract.end_date <= end_date_limit,
                    Contract.status.in_(["signed", "sent"]),
                )
            )
            .order_by(Contract.end_date)
        )
        contracts = list(result.scalars().all())

        for contract in contracts:
            d_day = (contract.end_date - today).days
            employee_name = contract.employee.name if contract.employee else "알 수 없음"

            severity = "critical" if d_day <= 7 else "warning"

            events.append({
                "id": f"contract_expiry_{contract.id}",
                "event_type": "contract_expiry",
                "title": f"{employee_name} 계약 만료 D-{d_day}",
                "description": f"{employee_name}님의 근로계약이 {contract.end_date.strftime('%Y-%m-%d')}에 만료됩니다. "
                               f"갱신 또는 종료 절차를 진행해주세요.",
                "event_date": contract.end_date.isoformat(),
                "d_day": d_day,
                "severity": severity,
                "related_employee_id": str(contract.employee_id),
                "related_employee_name": employee_name,
            })

        # 2) 급여 지급일 리마인더 (매월 25일)
        payroll_day = 25
        # 현재 월 25일 체크
        current_month_payroll = date(today.year, today.month, payroll_day)
        if current_month_payroll < today:
            # 이미 지났으면 다음 달
            if today.month == 12:
                current_month_payroll = date(today.year + 1, 1, payroll_day)
            else:
                current_month_payroll = date(today.year, today.month + 1, payroll_day)

        if current_month_payroll <= end_date_limit:
            d_day = (current_month_payroll - today).days
            severity = "warning" if d_day <= 7 else "info"

            events.append({
                "id": f"payroll_date_{current_month_payroll.year}_{current_month_payroll.month:02d}",
                "event_type": "payroll_date",
                "title": f"{current_month_payroll.month}월 급여 지급일 D-{d_day}",
                "description": f"{current_month_payroll.strftime('%Y-%m-%d')} 급여 지급 예정입니다. 급여 계산을 완료해주세요.",
                "event_date": current_month_payroll.isoformat(),
                "d_day": d_day,
                "severity": severity,
                "related_employee_id": None,
                "related_employee_name": None,
            })

        # D-Day 순 정렬 (임박한 것부터)
        events.sort(key=lambda e: e.get("d_day", 999) if e.get("d_day") is not None else 999)
        return events

    async def get_risk_score_history(
        self, company_id: uuid.UUID, months: int = 6
    ) -> list[dict]:
        """
        월별 리스크 스코어 변화 (간이 계산)

        과거 데이터가 별도 저장되어 있지 않으므로,
        현재 시점의 데이터를 기반으로 현재 달만 실제 계산하고,
        이전 달들은 개략적으로 추정합니다.
        실제 운영에서는 월말 스냅샷 테이블 도입을 권장합니다.
        """
        company = await self._get_company(company_id)
        today = date.today()
        history: list[dict] = []

        # 현재 달 스코어 계산
        current_score_data = await self.calculate_risk_score(company_id)
        current_score = current_score_data["score"]

        for i in range(months - 1, -1, -1):
            # 과거 월 계산
            target_month = today.month - i
            target_year = today.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1

            if i == 0:
                # 현재 달은 실제 스코어
                score = current_score
            else:
                # 이전 달들은 현재 스코어와 동일하게 (과거 데이터 없음)
                # 실제로는 스냅샷 테이블에서 조회
                score = current_score

            history.append({
                "year": target_year,
                "month": target_month,
                "score": score,
                "level": _get_score_level(score),
            })

        return history
