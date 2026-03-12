# Payslip 리포지토리
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal
from datetime import datetime, date
import uuid

from app.db.models import Payslip, Employee, Company


class PayslipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        employee_id: uuid.UUID,
        company_id: uuid.UUID,
        year: int,
        month: int,
        base_salary: Decimal,
        weekly_allowance: Decimal = Decimal("0"),
        overtime_pay: Decimal = Decimal("0"),
        night_pay: Decimal = Decimal("0"),
        holiday_pay: Decimal = Decimal("0"),
        meal_allowance: Decimal = Decimal("0"),
        transport_allowance: Decimal = Decimal("0"),
        national_pension: Decimal = Decimal("0"),
        health_insurance: Decimal = Decimal("0"),
        long_term_care: Decimal = Decimal("0"),
        employment_insurance: Decimal = Decimal("0"),
        income_tax: Decimal = Decimal("0"),
        local_income_tax: Decimal = Decimal("0"),
    ) -> Payslip:
        """급여명세서 생성"""
        total_payment = (
            base_salary + weekly_allowance + overtime_pay + night_pay +
            holiday_pay + meal_allowance + transport_allowance
        )
        total_deduction = (
            national_pension + health_insurance + long_term_care +
            employment_insurance + income_tax + local_income_tax
        )
        net_pay = total_payment - total_deduction

        payslip = Payslip(
            employee_id=employee_id,
            company_id=company_id,
            pay_year=year,
            pay_month=month,
            base_pay=base_salary,
            holiday_pay=weekly_allowance,  # 주휴수당은 holiday_pay 컬럼 사용
            overtime_pay=overtime_pay,
            night_pay=night_pay,
            holiday_work_pay=holiday_pay,  # 휴일근로수당
            meal_allowance=meal_allowance,
            transport_allowance=transport_allowance,
            gross_pay=total_payment,
            national_pension=national_pension,
            health_insurance=health_insurance,
            long_term_care=long_term_care,
            employment_insurance=employment_insurance,
            income_tax=income_tax,
            local_income_tax=local_income_tax,
            total_deduction=total_deduction,
            net_pay=net_pay,
            send_status="pending",
        )
        self.db.add(payslip)
        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def get_by_id(self, payslip_id: uuid.UUID) -> Payslip | None:
        """ID로 급여명세서 조회"""
        result = await self.db.execute(
            select(Payslip)
            .options(selectinload(Payslip.employee))
            .where(Payslip.id == payslip_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_company(
        self, payslip_id: uuid.UUID, company_id: uuid.UUID
    ) -> Payslip | None:
        """ID와 회사 ID로 급여명세서 조회"""
        result = await self.db.execute(
            select(Payslip)
            .options(selectinload(Payslip.employee))
            .where(and_(Payslip.id == payslip_id, Payslip.company_id == company_id))
        )
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: uuid.UUID,
        year: int | None = None,
        month: int | None = None,
        employee_id: uuid.UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Payslip]:
        """회사별 급여명세서 목록 조회"""
        query = (
            select(Payslip)
            .options(selectinload(Payslip.employee))
            .where(Payslip.company_id == company_id)
            .order_by(Payslip.pay_year.desc(), Payslip.pay_month.desc())
        )

        if year is not None:
            query = query.where(Payslip.pay_year == year)
        if month is not None:
            query = query.where(Payslip.pay_month == month)
        if employee_id is not None:
            query = query.where(Payslip.employee_id == employee_id)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_by_employee(
        self, employee_id: uuid.UUID, limit: int = 100
    ) -> list[Payslip]:
        """직원별 급여명세서 목록 조회 (히스토리)"""
        result = await self.db.execute(
            select(Payslip)
            .options(selectinload(Payslip.employee))
            .where(Payslip.employee_id == employee_id)
            .order_by(Payslip.pay_year.desc(), Payslip.pay_month.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_send_status(
        self,
        payslip_id: uuid.UUID,
        status: str,
        sent_via: str | None = None,
    ) -> Payslip | None:
        """발송 상태 업데이트"""
        payslip = await self.get_by_id(payslip_id)
        if payslip:
            payslip.send_status = status
            if status == "sent":
                payslip.sent_at = datetime.utcnow()
                payslip.sent_via = sent_via
            await self.db.commit()
            await self.db.refresh(payslip)
        return payslip

    async def check_employee_in_company(
        self, employee_id: uuid.UUID, company_id: uuid.UUID
    ) -> Employee | None:
        """직원이 해당 회사 소속인지 확인"""
        result = await self.db.execute(
            select(Employee).where(
                and_(Employee.id == employee_id, Employee.company_id == company_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_company_by_id(self, company_id: uuid.UUID) -> Company | None:
        """회사 정보 조회"""
        result = await self.db.execute(
            select(Company).where(Company.id == company_id)
        )
        return result.scalar_one_or_none()
