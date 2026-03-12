"""급여 계산 서비스"""
from decimal import Decimal, ROUND_DOWN, getcontext
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.models.employee import Employee
from app.db.models.salary import Payslip
from app.core.exceptions import NotFoundError


# Decimal 정밀도 설정
getcontext().prec = 20


class PayrollService:
    """급여 계산 서비스"""

    # 사회보험 요율 (문자열로 저장하여 정밀도 유지)
    NATIONAL_PENSION_RATE = Decimal("0.045")  # 4.5%
    HEALTH_INSURANCE_RATE = Decimal("0.03545")  # 3.545%
    LONG_TERM_CARE_RATE = Decimal("0.1295")  # 12.95% (건강보험료의 12.95%)
    EMPLOYMENT_INSURANCE_RATE = Decimal("0.009")  # 0.9%
    LOCAL_INCOME_TAX_RATE = Decimal("0.1")  # 10%

    # 근로기준법 요율
    OVERTIME_RATE = Decimal("1.5")  # 연장수당 1.5배
    NIGHT_RATE = Decimal("0.5")  # 야간수당 0.5배 (추가분)
    HOLIDAY_RATE_NORMAL = Decimal("1.5")  # 휴일수당 8시간 이내 1.5배
    HOLIDAY_RATE_OVER = Decimal("2.0")  # 휴일수당 8시간 초과 2.0배

    # 주 근로시간 기준 (월 209시간 = 52주 × 40시간 / 12개월)
    MONTHLY_HOURS = Decimal("209")

    @staticmethod
    def truncate_to_10_won(value: Decimal) -> int:
        """10원 미만 절사 (10원 단위로 내림)"""
        # 10으로 나누고 소수점 이하 절사 후 다시 10을 곱함
        return int((value / Decimal("10")).to_integral_value(rounding=ROUND_DOWN) * Decimal("10"))

    @staticmethod
    def calculate_hourly_wage(base_wage: Decimal) -> Decimal:
        """통상시급 계산

        통상시급 = 기본급 / 월 소정근로시간
        """
        if base_wage <= 0:
            raise ValueError("기본급은 0보다 커야 합니다.")
        return base_wage / PayrollService.MONTHLY_HOURS

    @staticmethod
    def calculate_overtime_pay(base_wage: Decimal, overtime_minutes: int) -> int:
        """연장수당 계산

        연장수당 = (기본급 / 209) × 연장시간 × 1.5
        """
        if overtime_minutes <= 0:
            return 0

        hourly_wage = PayrollService.calculate_hourly_wage(base_wage)
        overtime_hours = Decimal(overtime_minutes) / Decimal("60")
        overtime_pay = hourly_wage * overtime_hours * PayrollService.OVERTIME_RATE
        return PayrollService.truncate_to_10_won(overtime_pay)

    @staticmethod
    def calculate_night_pay(base_wage: Decimal, night_minutes: int) -> int:
        """야간수당 계산

        야간수당 = (기본급 / 209) × 야간시간 × 0.5
        """
        if night_minutes <= 0:
            return 0

        hourly_wage = PayrollService.calculate_hourly_wage(base_wage)
        night_hours = Decimal(night_minutes) / Decimal("60")
        night_pay = hourly_wage * night_hours * PayrollService.NIGHT_RATE
        return PayrollService.truncate_to_10_won(night_pay)

    @staticmethod
    def calculate_holiday_pay(base_wage: Decimal, holiday_minutes: int) -> int:
        """휴일수당 계산

        휴일수당 = (기본급 / 209) × 휴일시간 × 요율
        - 8시간 이내: 1.5배
        - 8시간 초과: 2.0배
        """
        if holiday_minutes <= 0:
            return 0

        hourly_wage = PayrollService.calculate_hourly_wage(base_wage)
        holiday_hours = Decimal(holiday_minutes) / Decimal("60")

        # 8시간 기준 (480분)
        normal_hours = min(holiday_hours, Decimal("8"))
        over_hours = max(holiday_hours - Decimal("8"), Decimal("0"))

        normal_pay = hourly_wage * normal_hours * PayrollService.HOLIDAY_RATE_NORMAL
        over_pay = hourly_wage * over_hours * PayrollService.HOLIDAY_RATE_OVER

        total_pay = normal_pay + over_pay
        return PayrollService.truncate_to_10_won(total_pay)

    @staticmethod
    def calculate_social_insurance(taxable_amount: Decimal) -> tuple[int, int, int]:
        """사회보험료 계산 (국민연금, 건강보험, 장기요양보험)

        Args:
            taxable_amount: 과세소득 (비과세 금액 제외)

        Returns:
            (국민연금, 건강보험, 장기요양보험)
        """
        # 기준소득월액 계산 (과세소득 기준)
        standard_income = taxable_amount

        # 국민연금 = 기준소득월액 × 4.5%
        national_pension = standard_income * PayrollService.NATIONAL_PENSION_RATE

        # 건강보험 = 보수월액 × 3.545%
        health_insurance = standard_income * PayrollService.HEALTH_INSURANCE_RATE

        # 장기요양보험 = 건강보험료 × 12.95%
        long_term_care = health_insurance * PayrollService.LONG_TERM_CARE_RATE

        return (
            PayrollService.truncate_to_10_won(national_pension),
            PayrollService.truncate_to_10_won(health_insurance),
            PayrollService.truncate_to_10_won(long_term_care),
        )

    @staticmethod
    def calculate_employment_insurance(gross_pay: Decimal) -> int:
        """고용보험료 계산

        고용보험 = 월보수 × 0.9%
        """
        employment_insurance = gross_pay * PayrollService.EMPLOYMENT_INSURANCE_RATE
        return PayrollService.truncate_to_10_won(employment_insurance)

    @staticmethod
    def calculate_income_tax(
        taxable_income: Decimal,
        family_count: int,
        pension: int,
        health: int,
        long_term: int,
    ) -> tuple[int, int]:
        """소득세 및 지방소득세 계산

        간이세액표 기준 계산 (2024년 기준)

        Args:
            taxable_income: 과세표준 (지급액 - 비과세 - 인적공제 - 연금보험료 - 건강보험료 - 장기요양보험료)
            family_count: 가족 수 (본인 포함)
            pension: 국민연금료
            health: 건강보험료
            long_term: 장기요양보험료

        Returns:
            (소득세, 지방소득세)
        """
        # 인적공제 (본인 1인 + 가족 수 - 1)
        basic_deduction = Decimal("1500000")  # 기본공제 150만원
        personal_deduction = basic_deduction * Decimal(family_count)

        # 사회보험료 공제
        social_insurance_deduction = Decimal(str(pension + health + long_term))

        # 과세표준 계산
        tax_base = max(taxable_income - personal_deduction - social_insurance_deduction, Decimal("0"))

        # 간이세액표 기준 소득세 계산
        if tax_base <= Decimal("0"):
            income_tax = Decimal("0")
        elif tax_base <= Decimal("12000000"):
            income_tax = tax_base * Decimal("0.06")
        elif tax_base <= Decimal("46000000"):
            income_tax = tax_base * Decimal("0.15") - Decimal("1080000")
        elif tax_base <= Decimal("88000000"):
            income_tax = tax_base * Decimal("0.24") - Decimal("5220000")
        elif tax_base <= Decimal("150000000"):
            income_tax = tax_base * Decimal("0.35") - Decimal("14900000")
        elif tax_base <= Decimal("300000000"):
            income_tax = tax_base * Decimal("0.38") - Decimal("19400000")
        elif tax_base <= Decimal("500000000"):
            income_tax = tax_base * Decimal("0.40") - Decimal("25400000")
        elif tax_base <= Decimal("1000000000"):
            income_tax = tax_base * Decimal("0.42") - Decimal("35400000")
        else:
            income_tax = tax_base * Decimal("0.45") - Decimal("65400000")

        # 소득세 10원 미만 절사
        income_tax = PayrollService.truncate_to_10_won(income_tax)

        # 지방소득세 = 소득세 × 10%
        local_income_tax = PayrollService.truncate_to_10_won(Decimal(income_tax) * PayrollService.LOCAL_INCOME_TAX_RATE)

        return int(income_tax), int(local_income_tax)

    @classmethod
    def calculate_payroll(
        cls,
        employee_id: str,
        pay_year: int,
        pay_month: int,
        base_wage: Decimal,
        overtime_minutes: int,
        night_minutes: int,
        holiday_minutes: int,
        meal_allowance: Decimal,
        transport_allowance: Decimal,
        income_tax_family_count: int,
    ) -> dict[str, Any]:
        """급여 계산

        Returns:
            급여 계산 결과 딕셔너리
        """
        # 지급 항목 계산
        overtime_pay = cls.calculate_overtime_pay(base_wage, overtime_minutes)
        night_pay = cls.calculate_night_pay(base_wage, night_minutes)
        holiday_pay = cls.calculate_holiday_pay(base_wage, holiday_minutes)

        # 기타 수당 10원 단위 절사
        meal_allowance_int = cls.truncate_to_10_won(meal_allowance)
        transport_allowance_int = cls.truncate_to_10_won(transport_allowance)

        # 비과세 항목 (식대 100,000원까지 비과세)
        tax_free_meal = min(meal_allowance_int, 100000)
        tax_free_transport = transport_allowance_int

        # 총 지급액 (과세소득 계산용)
        gross_pay = (
            int(base_wage) +
            overtime_pay +
            night_pay +
            holiday_pay +
            meal_allowance_int +
            transport_allowance_int
        )

        # 과세소득 (비과세 제외)
        taxable_income = gross_pay - tax_free_meal - tax_free_transport

        # 사회보험료 계산
        national_pension, health_insurance, long_term_care = cls.calculate_social_insurance(
            Decimal(str(taxable_income))
        )

        # 고용보험료 계산
        employment_insurance = cls.calculate_employment_insurance(Decimal(str(gross_pay)))

        # 소득세 및 지방소득세 계산
        income_tax, local_income_tax = cls.calculate_income_tax(
            Decimal(str(taxable_income)),
            income_tax_family_count,
            national_pension,
            health_insurance,
            long_term_care,
        )

        # 총 공제액
        total_deduction = (
            national_pension +
            health_insurance +
            long_term_care +
            employment_insurance +
            income_tax +
            local_income_tax
        )

        # 실수령액
        net_pay = gross_pay - total_deduction

        return {
            "employee_id": employee_id,
            "pay_year": pay_year,
            "pay_month": pay_month,
            # 지급 항목
            "base_wage": int(base_wage),
            "overtime_pay": overtime_pay,
            "night_pay": night_pay,
            "holiday_pay": holiday_pay,
            "meal_allowance": meal_allowance_int,
            "transport_allowance": transport_allowance_int,
            "total_gross": gross_pay,
            # 공제 항목
            "national_pension": national_pension,
            "health_insurance": health_insurance,
            "long_term_care": long_term_care,
            "employment_insurance": employment_insurance,
            "income_tax": income_tax,
            "local_income_tax": local_income_tax,
            "total_deduction": total_deduction,
            # 실수령액
            "net_pay": net_pay,
        }

    @staticmethod
    def get_rates() -> dict[str, str]:
        """급여 요율 조회"""
        return {
            # 사회보험 요율
            "national_pension_rate": "0.045",
            "health_insurance_rate": "0.03545",
            "long_term_care_rate": "0.1295",
            "employment_insurance_rate": "0.009",
            "local_income_tax_rate": "0.1",
            # 근로기준법 요율
            "overtime_rate": "1.5",
            "night_rate": "0.5",
            "holiday_rate_normal": "1.5",
            "holiday_rate_over": "2.0",
        }

    @staticmethod
    async def verify_employee_access(
        db: AsyncSession,
        user_company_id: str,
        employee_id: str
    ) -> Employee:
        """직원 접근 권한 확인

        Raises:
            NotFoundError: 직원을 찾을 수 없거나 권한이 없는 경우
        """
        stmt = select(Employee).where(
            Employee.id == uuid.UUID(employee_id),
            Employee.company_id == uuid.UUID(user_company_id),
            Employee.is_active == True
        )
        result = await db.execute(stmt)
        employee = result.scalar_one_or_none()

        if employee is None:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        return employee
