# Payslip 서비스
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from datetime import date
import uuid
import logging

from app.repositories.payslip_repo import PayslipRepository
from app.core.exceptions import NotFoundError, ForbiddenError
from app.db.models import Payslip
from app.services.notification_service import EmailService, KakaoAlimtalkService
from app.services.pdf_service import PayslipPDFService

logger = logging.getLogger(__name__)


class PayslipService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PayslipRepository(db)

    async def create_payslip(
        self,
        company_id: uuid.UUID,
        employee_id: uuid.UUID,
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
    ) -> dict:
        """급여명세서 생성"""
        # 직원이 해당 회사 소속인지 확인
        employee = await self.repo.check_employee_in_company(employee_id, company_id)
        if not employee:
            raise NotFoundError(message="직원을 찾을 수 없습니다.")

        # 급여명세서 생성
        payslip = await self.repo.create(
            employee_id=employee_id,
            company_id=company_id,
            year=year,
            month=month,
            base_salary=base_salary,
            weekly_allowance=weekly_allowance,
            overtime_pay=overtime_pay,
            night_pay=night_pay,
            holiday_pay=holiday_pay,
            meal_allowance=meal_allowance,
            transport_allowance=transport_allowance,
            national_pension=national_pension,
            health_insurance=health_insurance,
            long_term_care=long_term_care,
            employment_insurance=employment_insurance,
            income_tax=income_tax,
            local_income_tax=local_income_tax,
        )

        return await self._to_response(payslip)

    async def get_payslip(
        self, payslip_id: uuid.UUID, company_id: uuid.UUID
    ) -> dict:
        """급여명세서 상세 조회"""
        payslip = await self.repo.get_by_id_and_company(payslip_id, company_id)
        if not payslip:
            raise NotFoundError(message="급여명세서를 찾을 수 없습니다.")

        return await self._to_response(payslip)

    async def list_payslips(
        self,
        company_id: uuid.UUID,
        year: int | None = None,
        month: int | None = None,
        employee_id: uuid.UUID | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> list[dict]:
        """급여명세서 목록 조회"""
        offset = (page - 1) * per_page
        payslips = await self.repo.list_by_company(
            company_id=company_id,
            year=year,
            month=month,
            employee_id=employee_id,
            limit=per_page,
            offset=offset,
        )
        return [await self._to_response(p) for p in payslips]

    async def list_employee_payslips(
        self,
        employee_id: uuid.UUID,
        company_id: uuid.UUID,
        limit: int = 24,
    ) -> list[dict]:
        """직원별 급여 히스토리 조회"""
        # 직원이 해당 회사 소속인지 확인
        employee = await self.repo.check_employee_in_company(employee_id, company_id)
        if not employee:
            raise NotFoundError(message="직원을 찾을 수 없거나 접근 권한이 없습니다.")

        payslips = await self.repo.list_by_employee(employee_id, limit=limit)
        return [await self._to_response(p) for p in payslips]

    async def send_payslip(
        self,
        payslip_id: uuid.UUID,
        company_id: uuid.UUID,
        method: str = "email",
        email: str | None = None,
    ) -> dict:
        """급여명세서 발송

        발송 방식:
        - email: 이메일 발송
        - kakao: 카카오 알림톡 발송 (실패 시 이메일 fallback, 최대 3회 재시도)
        - both: 이메일 + 카카오 알림톡 모두 발송 시도

        발송 결과에 따라 DB send_status를 sent/failed로 업데이트합니다.
        """
        payslip = await self.repo.get_by_id_and_company(payslip_id, company_id)
        if not payslip:
            raise NotFoundError(message="급여명세서를 찾을 수 없습니다.")

        company = await self.repo.get_company_by_id(payslip.company_id)
        employee = payslip.employee

        # 응답 dict 생성 (PDF 생성에 사용)
        payslip_data = await self._to_response(payslip)

        # PDF 생성
        pdf_content = self._generate_pdf(payslip_data)

        # 발송 대상 이메일 결정 (파라미터 > 직원 이메일)
        target_email: str | None = email or (employee.email if employee else None)
        company_name = company.business_name if company else ""
        employee_name = employee.name if employee else ""
        net_salary = str(int(payslip.net_pay))

        sent = False
        sent_via_result: str | None = None

        if method in ("email", "both"):
            # 이메일 발송
            if target_email:
                email_sent = await EmailService.send_payslip_email(
                    to_email=target_email,
                    employee_name=employee_name,
                    company_name=company_name,
                    year=payslip.pay_year,
                    month=payslip.pay_month,
                    pdf_content=pdf_content,
                )
                if email_sent:
                    sent = True
                    sent_via_result = "email"
            else:
                logger.warning(
                    "이메일 발송 대상 없음: payslip_id=%s", payslip_id
                )

        if method in ("kakao", "both"):
            # 카카오 알림톡 발송 (최대 3회 재시도)
            phone_number: str = (
                employee.phone if (employee and hasattr(employee, "phone") and employee.phone) else ""
            )
            kakao_sent = False
            max_retries = 3

            for attempt in range(1, max_retries + 1):
                kakao_sent = await KakaoAlimtalkService.send_payslip_notification(
                    phone_number=phone_number,
                    employee_name=employee_name,
                    company_name=company_name,
                    year=payslip.pay_year,
                    month=payslip.pay_month,
                    net_salary=net_salary,
                )
                if kakao_sent:
                    sent = True
                    if sent_via_result is None:
                        sent_via_result = "kakao"
                    break
                logger.warning(
                    "카카오 알림톡 발송 실패 (%d/%d): payslip_id=%s",
                    attempt, max_retries, payslip_id,
                )

            # 카카오 3회 실패 시 이메일 fallback
            if not kakao_sent and method == "kakao" and target_email:
                logger.info(
                    "카카오 알림톡 발송 최종 실패, 이메일 fallback 시도: payslip_id=%s",
                    payslip_id,
                )
                email_fallback = await EmailService.send_payslip_email(
                    to_email=target_email,
                    employee_name=employee_name,
                    company_name=company_name,
                    year=payslip.pay_year,
                    month=payslip.pay_month,
                    pdf_content=pdf_content,
                )
                if email_fallback:
                    sent = True
                    sent_via_result = "email"

        # 발송 결과를 DB에 반영
        final_status = "sent" if sent else "failed"
        updated_payslip = await self.repo.update_send_status(
            payslip_id, final_status, sent_via_result
        )

        return await self._to_response(updated_payslip)

    async def get_payslip_pdf(
        self, payslip_id: uuid.UUID, company_id: uuid.UUID
    ) -> bytes:
        """급여명세서 PDF 생성"""
        payslip = await self.repo.get_by_id_and_company(payslip_id, company_id)
        if not payslip:
            raise NotFoundError(message="급여명세서를 찾을 수 없습니다.")

        payslip_data = await self._to_response(payslip)
        return self._generate_pdf(payslip_data)

    def _generate_pdf(self, payslip_data: dict) -> bytes:
        """ReportLab으로 급여명세서 PDF 생성"""
        return PayslipPDFService.generate(payslip_data)

    async def _to_response(self, payslip: Payslip) -> dict:
        """Payslip 모델을 응답 dict로 변환"""
        company = await self.repo.get_company_by_id(payslip.company_id)

        return {
            "id": str(payslip.id),
            "employee_id": str(payslip.employee_id),
            "employee_name": payslip.employee.name if payslip.employee else "",
            "company_name": company.business_name if company else "",
            "year": payslip.pay_year,
            "month": payslip.pay_month,
            "payment_date": None,  # 별도 필드로 관리 필요시 추가
            # 지급 항목 (int로 직렬화하여 JSON 과학적 표기법 방지)
            "base_salary": int(payslip.base_pay),
            "weekly_allowance": int(payslip.holiday_pay),  # 주휴수당
            "overtime_pay": int(payslip.overtime_pay),
            "night_pay": int(payslip.night_pay),
            "holiday_pay": int(payslip.holiday_work_pay),  # 휴일근로수당
            "meal_allowance": int(payslip.meal_allowance),
            "transport_allowance": int(payslip.transport_allowance),
            "total_payment": int(payslip.gross_pay),
            # 공제 항목
            "national_pension": int(payslip.national_pension),
            "health_insurance": int(payslip.health_insurance),
            "long_term_care": int(payslip.long_term_care),
            "employment_insurance": int(payslip.employment_insurance),
            "income_tax": int(payslip.income_tax),
            "local_income_tax": int(payslip.local_income_tax),
            "total_deduction": int(payslip.total_deduction),
            # 실수령액
            "net_salary": int(payslip.net_pay),
            # 발송 상태
            "send_status": payslip.send_status,
            "sent_at": payslip.sent_at,
            "sent_via": payslip.sent_via,
            "created_at": payslip.created_at,
        }
