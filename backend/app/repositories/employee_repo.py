# Employee Repository
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models.employee import Employee


class EmployeeRepository:
    """Employee CRUD 작업을 담당하는 Repository"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, employee_id: uuid.UUID | str) -> Optional[Employee]:
        """ID로 직원 조회"""
        if isinstance(employee_id, str):
            employee_id = uuid.UUID(employee_id)

        stmt = select(Employee).where(Employee.id == employee_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_company(
        self,
        employee_id: uuid.UUID | str,
        company_id: uuid.UUID | str
    ) -> Optional[Employee]:
        """회사 ID와 직원 ID로 직원 조회"""
        if isinstance(employee_id, str):
            employee_id = uuid.UUID(employee_id)
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == company_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: uuid.UUID | str,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Employee]:
        """회사별 직원 목록 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(Employee).where(Employee.company_id == company_id)

        if is_active is not None:
            stmt = stmt.where(Employee.is_active == is_active)

        stmt = stmt.order_by(Employee.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_company(
        self,
        company_id: uuid.UUID | str,
        is_active: Optional[bool] = None
    ) -> int:
        """회사별 직원 수 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        from sqlalchemy import func
        stmt = select(func.count(Employee.id)).where(Employee.company_id == company_id)

        if is_active is not None:
            stmt = stmt.where(Employee.is_active == is_active)

        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def create(
        self,
        company_id: uuid.UUID,
        name: str,
        nationality: str,
        employment_type: str,
        hire_date,
        id_number: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_account: Optional[str] = None
    ) -> Employee:
        """직원 생성"""
        employee = Employee(
            company_id=company_id,
            user_id=user_id,
            name=name,
            id_number=id_number,
            nationality=nationality,
            employment_type=employment_type,
            department=department,
            position=position,
            hire_date=hire_date,
            phone=phone,
            email=email,
            bank_name=bank_name,
            bank_account=bank_account,
            is_active=True
        )
        self.db.add(employee)
        await self.db.flush()
        await self.db.refresh(employee)
        return employee

    async def update(
        self,
        employee: Employee,
        name: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_account: Optional[str] = None,
        is_active: Optional[bool] = None,
        resign_date: Optional = None
    ) -> Employee:
        """직원 정보 수정"""
        if name is not None:
            employee.name = name
        if department is not None:
            employee.department = department
        if position is not None:
            employee.position = position
        if phone is not None:
            employee.phone = phone
        if email is not None:
            employee.email = email
        if bank_name is not None:
            employee.bank_name = bank_name
        if bank_account is not None:
            employee.bank_account = bank_account
        if is_active is not None:
            employee.is_active = is_active
        if resign_date is not None:
            employee.resign_date = resign_date

        await self.db.flush()
        await self.db.refresh(employee)
        return employee

    async def soft_delete(self, employee: Employee, resign_date=None) -> Employee:
        """직원 퇴직 처리 (Soft Delete)"""
        employee.is_active = False
        if resign_date:
            employee.resign_date = resign_date
        await self.db.flush()
        await self.db.refresh(employee)
        return employee
