# 직원 서비스
from typing import Optional, Any
from datetime import date, datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.db.models.employee import Employee
from app.repositories.employee_repo import EmployeeRepository
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError


class EmployeeService:
    """직원 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession, redis: aioredis.Redis) -> None:
        self.db = db
        self.repo = EmployeeRepository(db)
        self.redis = redis

    async def create_employee(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        nationality: str,
        employment_type: str,
        hire_date: date,
        id_number: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_account: Optional[str] = None
    ) -> dict[str, Any]:
        """
        직원 등록

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID
            name: 이름
            nationality: 국적
            employment_type: 고용형태
            hire_date: 입사일
            id_number: 주민등록번호
            department: 부서
            position: 직급
            phone: 전화번호
            email: 이메일
            bank_name: 은행명
            bank_account: 계좌번호

        Returns:
            생성된 직원 정보

        Raises:
            NotFoundError: 사업장을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장에 접근
        """
        # 사업장 소유권 확인 (간단 확인 - 실제로는 회사 확인 로직 추가)
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 직원을 등록할 수 없습니다.")

        # 직원 생성
        employee = await self.repo.create(
            company_id=company_id,
            name=name,
            nationality=nationality,
            employment_type=employment_type,
            hire_date=hire_date,
            id_number=id_number,
            department=department,
            position=position,
            phone=phone,
            email=email,
            bank_name=bank_name,
            bank_account=bank_account
        )

        await self.db.commit()

        return self._employee_to_dict(employee)

    async def get_employees(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        is_active: Optional[bool] = None,
        limit: int = 20,
        skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        직원 목록 조회

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)
            is_active: 활성 여부 필터
            limit: 페이지 크기
            skip: 건너뛸 수

        Returns:
            직원 목록

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

        employees = await self.repo.list_by_company(
            company_id=company_id,
            is_active=is_active,
            skip=skip,
            limit=limit
        )

        return [self._employee_to_list_item(e) for e in employees]

    async def get_employee(
        self,
        employee_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> dict[str, Any]:
        """
        직원 상세 조회

        Args:
            employee_id: 직원 ID
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)

        Returns:
            직원 상세 정보

        Raises:
            NotFoundError: 직원을 찾을 수 없음
            ForbiddenError: 다른 사용자의 직원 접근
        """
        # 사업장 소유권 확인
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 접근할 수 없습니다.")

        employee = await self.repo.get_by_id_and_company(employee_id, company_id)

        if employee is None:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        return self._employee_to_dict(employee)

    async def update_employee(
        self,
        employee_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_account: Optional[str] = None,
        is_active: Optional[bool] = None,
        resign_date: Optional[date] = None
    ) -> dict[str, Any]:
        """
        직원 정보 수정

        Args:
            employee_id: 직원 ID
            company_id: 사업장 ID
            user_id: 요청 사용자 ID
            name: 이름
            department: 부서
            position: 직급
            phone: 전화번호
            email: 이메일
            bank_name: 은행명
            bank_account: 계좌번호
            is_active: 활성 여부
            resign_date: 퇴사일

        Returns:
            수정된 직원 정보

        Raises:
            NotFoundError: 직원을 찾을 수 없음
            ForbiddenError: 다른 사용자의 직원 수정
        """
        # 사업장 소유권 확인
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 직원을 수정할 수 없습니다.")

        employee = await self.repo.get_by_id_and_company(employee_id, company_id)

        if employee is None:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        employee = await self.repo.update(
            employee=employee,
            name=name,
            department=department,
            position=position,
            phone=phone,
            email=email,
            bank_name=bank_name,
            bank_account=bank_account,
            is_active=is_active,
            resign_date=resign_date
        )

        await self.db.commit()

        return self._employee_to_dict(employee)

    async def resign_employee(
        self,
        employee_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        resign_date: Optional[date] = None
    ) -> dict[str, Any]:
        """
        직원 퇴직 처리

        Args:
            employee_id: 직원 ID
            company_id: 사업장 ID
            user_id: 요청 사용자 ID
            resign_date: 퇴사일 (None이면 오늘)

        Returns:
            퇴직 처리된 직원 정보

        Raises:
            NotFoundError: 직원을 찾을 수 없음
            ForbiddenError: 다른 사용자의 직원 퇴직 처리
            ValidationError: 이미 퇴직한 직원
        """
        # 사업장 소유권 확인
        from app.repositories.company_repo import CompanyRepository
        company_repo = CompanyRepository(self.db)

        company = await company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 직원을 퇴직 처리할 수 없습니다.")

        employee = await self.repo.get_by_id_and_company(employee_id, company_id)

        if employee is None:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        if not employee.is_active:
            raise ValidationError(
                message="이미 퇴직한 직원입니다.",
                details=[{"field": "employee_id", "message": "이미 퇴직 처리된 직원입니다."}]
            )

        # 퇴사일이 없으면 오늘로 설정
        if resign_date is None:
            resign_date = datetime.utcnow().date()

        employee = await self.repo.soft_delete(employee, resign_date)

        await self.db.commit()

        return self._employee_to_dict(employee)

    def _employee_to_dict(self, employee: Employee) -> dict[str, Any]:
        """Employee 모델을 딕셔너리로 변환"""
        return {
            "id": str(employee.id),
            "company_id": str(employee.company_id),
            "user_id": str(employee.user_id) if employee.user_id else None,
            "name": employee.name,
            "nationality": employee.nationality,
            "employment_type": employee.employment_type,
            "department": employee.department,
            "position": employee.position,
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "resign_date": employee.resign_date.isoformat() if employee.resign_date else None,
            "is_active": employee.is_active,
            "phone": employee.phone,
            "email": employee.email,
            "bank_name": employee.bank_name,
            "bank_account": employee.bank_account,
            "created_at": employee.created_at.isoformat() if employee.created_at else None,
            "updated_at": employee.updated_at.isoformat() if employee.updated_at else None
        }

    def _employee_to_list_item(self, employee: Employee) -> dict[str, Any]:
        """Employee 모델을 목록 아이템으로 변환"""
        return {
            "id": str(employee.id),
            "name": employee.name,
            "nationality": employee.nationality,
            "employment_type": employee.employment_type,
            "department": employee.department,
            "position": employee.position,
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "is_active": employee.is_active
        }
