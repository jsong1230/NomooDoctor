# 계약서 서비스
from typing import Optional
from datetime import date, datetime, timezone
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.db.models.contract import Contract
from app.repositories.contract_repo import ContractRepository
from app.repositories.employee_repo import EmployeeRepository
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError, AppError
from app.external.modusign_client import ModusignClient


# 2026년 최저임금 기준 (시급)
MINIMUM_WAGE_HOURLY = 10030
# 월 근무시간 기준 (연간 2090시간 / 12)
MONTHLY_WORKING_HOURS = 209


class ContractService:
    """계약서 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession, redis: aioredis.Redis) -> None:
        self.db = db
        self.repo = ContractRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.redis = redis

    def _validate_minimum_wage(
        self,
        wage_type: str,
        base_wage: float,
        work_hours_per_week: float
    ) -> None:
        """
        최저임금 검증

        Args:
            wage_type: 급여 타입 (monthly, hourly, daily)
            base_wage: 기본급
            work_hours_per_week: 주 근무시간

        Raises:
            ValidationError: 최저임금 미달 시
        """
        if wage_type == "hourly":
            hourly_wage = base_wage
            if hourly_wage < MINIMUM_WAGE_HOURLY:
                raise ValidationError(
                    message="최저임금 기준에 미달합니다.",
                    details=[
                        {
                            "field": "base_wage",
                            "message": f"시급 {hourly_wage}원은 최저임금 {MINIMUM_WAGE_HOURLY}원 미달입니다."
                        }
                    ]
                )
        elif wage_type == "monthly":
            # 월급의 경우 시급으로 환산하여 검증
            # 월 근무시간 기준: 209시간
            hourly_wage = base_wage / MONTHLY_WORKING_HOURS
            if hourly_wage < MINIMUM_WAGE_HOURLY:
                raise ValidationError(
                    message="최저임금 기준에 미달합니다.",
                    details=[
                        {
                            "field": "base_wage",
                            "message": f"월급 {base_wage:,}원은 시급 약 {int(hourly_wage):,}원으로 최저임금 {MINIMUM_WAGE_HOURLY}원 미달입니다."
                        }
                    ]
                )
        elif wage_type == "daily":
            # 일급의 경우 시급으로 환산하여 검증
            # 기준: 주 40시간 / 5일 = 일 8시간
            daily_hours = work_hours_per_week / 5 if work_hours_per_week else 8
            hourly_wage = base_wage / daily_hours
            if hourly_wage < MINIMUM_WAGE_HOURLY:
                raise ValidationError(
                    message="최저임금 기준에 미달합니다.",
                    details=[
                        {
                            "field": "base_wage",
                            "message": f"일급 {base_wage:,}원은 시급 약 {int(hourly_wage):,}원으로 최저임금 {MINIMUM_WAGE_HOURLY}원 미달입니다."
                        }
                    ]
                )

    async def create_contract(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        employee_id: uuid.UUID,
        contract_type: str,
        start_date: date,
        work_location: str,
        work_hours_per_week: float,
        work_start_time: str,
        work_end_time: str,
        break_minutes: int = 60,
        work_days: str = "월화수목금",
        wage_type: str = "monthly",
        base_wage: float = 0,
        meal_allowance: float = 0,
        transport_allowance: float = 0,
        probation_months: int = 0,
        probation_wage_rate: float = 1.0,
        nda_included: bool = False,
        non_compete_included: bool = False,
        end_date: date | None = None
    ) -> dict[str, any]:
        """
        계약서 생성

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID
            employee_id: 직원 ID
            contract_type: 계약 유형
            start_date: 계약 시작일
            work_location: 근무지
            work_hours_per_week: 주 근무시간
            work_start_time: 근무 시작 시간
            work_end_time: 근무 종료 시간
            break_minutes: 휴게시간(분)
            work_days: 근무 요일
            wage_type: 급여 유형
            base_wage: 기본급
            meal_allowance: 식대
            transport_allowance: 교통비
            probation_months: 수습기간(월)
            probation_wage_rate: 수습급여 비율
            nda_included: NDA 포함 여부
            non_compete_included: 경업금지 포함 여부
            end_date: 계약 종료일

        Returns:
            생성된 계약서 정보

        Raises:
            NotFoundError: 사업장 또는 직원을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장/직원 접근
            ValidationError: 최저임금 미달
        """
        # 사업장 소유권 확인
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 접근할 수 없습니다.")

        # 직원 소유권 확인
        employee = await self.employee_repo.get_by_id_and_company(employee_id, company_id)
        if employee is None:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        # 최저임금 검증
        self._validate_minimum_wage(wage_type, base_wage, work_hours_per_week)

        # 계약서 생성
        contract = await self.repo.create(
            company_id=company_id,
            employee_id=employee_id,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            work_location=work_location,
            work_hours_per_week=work_hours_per_week,
            work_start_time=work_start_time,
            work_end_time=work_end_time,
            break_minutes=break_minutes,
            work_days=work_days,
            wage_type=wage_type,
            base_wage=base_wage,
            meal_allowance=meal_allowance,
            transport_allowance=transport_allowance,
            probation_months=probation_months,
            probation_wage_rate=probation_wage_rate,
            nda_included=nda_included,
            non_compete_included=non_compete_included,
            status="draft",
            ai_generated=True,
            ai_model="gpt-4o-mini"
        )

        await self.db.commit()

        return self._contract_to_dict(contract)

    async def get_contracts(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        skip: int = 0
    ) -> list[dict[str, any]]:
        """
        계약서 목록 조회

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)
            employee_id: 직원 ID 필터
            status: 상태 필터
            limit: 페이지 크기
            skip: 건너뛸 수

        Returns:
            계약서 목록

        Raises:
            NotFoundError: 사업장을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장 접근
        """
        # 사업장 소유권 확인
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 접근할 수 없습니다.")

        contracts = await self.repo.list_by_company(
            company_id=company_id,
            employee_id=employee_id,
            status=status,
            skip=skip,
            limit=limit
        )

        # 직원 이름 조인하여 목록 변환
        result = []
        for contract in contracts:
            data = self._contract_to_dict(contract)
            # 직원 이름 추가
            if contract.employee:
                data["employee_name"] = contract.employee.name
            else:
                data["employee_name"] = None
            result.append(data)

        return result

    async def get_contract(
        self,
        contract_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> dict[str, any]:
        """
        계약서 상세 조회

        Args:
            contract_id: 계약서 ID
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)

        Returns:
            계약서 상세 정보

        Raises:
            NotFoundError: 사업장 또는 계약서를 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장 접근
        """
        # 사업장 소유권 확인
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 접근할 수 없습니다.")

        contract = await self.repo.get_by_id_and_company(contract_id, company_id)

        if contract is None:
            raise NotFoundError("계약서를 찾을 수 없습니다.")

        return self._contract_to_dict(contract)

    async def _verify_contract_access(
        self, contract_id: uuid.UUID, company_id: uuid.UUID, user_id: uuid.UUID
    ) -> Contract:
        """계약서 접근 권한 검증 후 계약서 반환"""
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)
        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")
        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 접근할 수 없습니다.")

        contract = await self.repo.get_by_id_and_company(contract_id, company_id)
        if contract is None:
            raise NotFoundError("계약서를 찾을 수 없습니다.")
        return contract

    async def send_sign_request(
        self,
        contract_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        signer_name: str,
        signer_email: str,
        signer_phone: Optional[str] = None,
    ) -> dict:
        """전자서명 요청 발송"""
        contract = await self._verify_contract_access(contract_id, company_id, user_id)

        if contract.status == "signed":
            raise AppError("이미 서명 완료된 계약서입니다.", code="E-9004", status_code=409)

        if contract.status != "draft":
            raise AppError("전자서명은 초안 상태의 계약서만 요청할 수 있습니다.", code="E-9002", status_code=400)

        async with ModusignClient() as client:
            result = await client.create_signing_request(
                document_title=f"근로계약서 - {signer_name}",
                pdf_url=contract.pdf_url or "",
                signer_name=signer_name,
                signer_email=signer_email,
                signer_phone=signer_phone,
            )

        contract.status = "sent"
        contract.sign_service_ref = result["document_id"]
        await self.db.commit()

        return {
            "contract_id": str(contract.id),
            "sign_service_ref": result["document_id"],
            "status": "sent",
            "signing_url": result["signing_url"],
        }

    async def get_sign_status(
        self,
        contract_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        """전자서명 상태 조회"""
        contract = await self._verify_contract_access(contract_id, company_id, user_id)

        if not contract.sign_service_ref:
            return {
                "contract_id": str(contract.id),
                "status": contract.status,
                "sign_service_ref": None,
                "signed_at": None,
            }

        # 모두싸인 API로 최신 상태 조회
        async with ModusignClient() as client:
            result = await client.get_document_status(contract.sign_service_ref)

        # 완료 상태면 DB 업데이트
        if result["status"] == "completed" and contract.status != "signed":
            contract.status = "signed"
            contract.signed_at = datetime.now(timezone.utc)
            await self.db.commit()

        return {
            "contract_id": str(contract.id),
            "status": contract.status,
            "sign_service_ref": contract.sign_service_ref,
            "signed_at": contract.signed_at.isoformat() if contract.signed_at else None,
        }

    async def handle_sign_webhook(self, document_id: str, completed_at: Optional[str] = None) -> bool:
        """모두싸인 웹훅 처리"""
        contract = await self.repo.get_by_sign_ref(document_id)
        if contract is None:
            return False

        if contract.status == "signed":
            return True  # 이미 처리됨

        contract.status = "signed"
        contract.signed_at = (
            datetime.fromisoformat(completed_at) if completed_at
            else datetime.now(timezone.utc)
        )
        await self.db.commit()
        return True

    async def get_signed_pdf(
        self,
        contract_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bytes:
        """서명된 PDF 다운로드"""
        contract = await self._verify_contract_access(contract_id, company_id, user_id)

        if contract.status != "signed":
            raise AppError("서명 완료된 계약서만 다운로드할 수 있습니다.", code="E-9005", status_code=400)

        if not contract.sign_service_ref:
            raise AppError("전자서명 정보가 없습니다.", code="E-9005", status_code=400)

        async with ModusignClient() as client:
            return await client.download_signed_pdf(contract.sign_service_ref)

    def _contract_to_dict(self, contract: Contract) -> dict[str, any]:
        """Contract 모델을 딕셔너리로 변환"""
        return {
            "id": str(contract.id),
            "company_id": str(contract.company_id),
            "employee_id": str(contract.employee_id),
            "contract_type": contract.contract_type,
            "start_date": contract.start_date.isoformat() if contract.start_date else None,
            "end_date": contract.end_date.isoformat() if contract.end_date else None,
            "work_location": contract.work_location,
            "work_hours_per_week": float(contract.work_hours_per_week),
            "work_start_time": contract.work_start_time.strftime("%H:%M") if contract.work_start_time else None,
            "work_end_time": contract.work_end_time.strftime("%H:%M") if contract.work_end_time else None,
            "break_minutes": contract.break_minutes,
            "work_days": contract.work_days,
            "wage_type": contract.wage_type,
            "base_wage": int(contract.base_wage),
            "meal_allowance": int(contract.meal_allowance),
            "transport_allowance": int(contract.transport_allowance),
            "probation_months": contract.probation_months,
            "probation_wage_rate": float(contract.probation_wage_rate),
            "nda_included": contract.nda_included,
            "non_compete_included": contract.non_compete_included,
            "status": contract.status,
            "docx_url": contract.docx_url,
            "pdf_url": contract.pdf_url,
            "ai_generated": contract.ai_generated,
            "ai_model": contract.ai_model,
            "signed_at": contract.signed_at.isoformat() if contract.signed_at else None,
            "sign_service_ref": contract.sign_service_ref,
            "version": contract.version,
            "created_at": contract.created_at.isoformat() if contract.created_at else None,
            "updated_at": contract.updated_at.isoformat() if contract.updated_at else None
        }
