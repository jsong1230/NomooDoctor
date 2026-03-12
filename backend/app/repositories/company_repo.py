# Company Repository
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.models.company import Company


class CompanyRepository:
    """Company CRUD 작업을 담당하는 Repository"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, company_id: uuid.UUID | str) -> Optional[Company]:
        """ID로 사업장 조회 (삭제된 사업장 제외)"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(Company).where(
            Company.id == company_id,
            Company.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_deleted(self, company_id: uuid.UUID | str) -> Optional[Company]:
        """ID로 사업장 조회 (삭제된 사업장 포함)"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(Company).where(Company.id == company_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_business_number(self, business_number: str) -> Optional[Company]:
        """사업자등록번호로 사업장 조회 (삭제된 사업장 제외)"""
        stmt = select(Company).where(
            Company.business_number == business_number,
            Company.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner(
        self,
        owner_id: uuid.UUID | str,
        skip: int = 0,
        limit: int = 20,
        is_deleted: bool = False
    ) -> List[Company]:
        """소유자별 사업장 목록 조회"""
        if isinstance(owner_id, str):
            owner_id = uuid.UUID(owner_id)

        stmt = select(Company).where(
            Company.owner_id == owner_id,
            Company.is_deleted == is_deleted
        ).order_by(Company.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_owner(self, owner_id: uuid.UUID | str, is_deleted: bool = False) -> int:
        """소유자별 사업장 수 조회"""
        if isinstance(owner_id, str):
            owner_id = uuid.UUID(owner_id)

        from sqlalchemy import func
        stmt = select(func.count(Company.id)).where(
            Company.owner_id == owner_id,
            Company.is_deleted == is_deleted
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def create(
        self,
        owner_id: uuid.UUID,
        business_name: str,
        business_number: str,
        representative_name: str,
        industry_type: str,
        employee_count: int = 0,
        address: Optional[str] = None,
        postal_code: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Company:
        """사업장 생성"""
        company = Company(
            owner_id=owner_id,
            business_name=business_name,
            business_number=business_number,
            representative_name=representative_name,
            industry_type=industry_type,
            employee_count=employee_count,
            address=address,
            postal_code=postal_code,
            phone=phone,
            is_deleted=False,
            work_rule_required=employee_count >= 10
        )
        self.db.add(company)
        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def update(
        self,
        company: Company,
        business_name: Optional[str] = None,
        representative_name: Optional[str] = None,
        industry_type: Optional[str] = None,
        employee_count: Optional[int] = None,
        address: Optional[str] = None,
        postal_code: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Company:
        """사업장 정보 수정 (business_number 제외)"""
        if business_name is not None:
            company.business_name = business_name
        if representative_name is not None:
            company.representative_name = representative_name
        if industry_type is not None:
            company.industry_type = industry_type
        if employee_count is not None:
            company.employee_count = employee_count
        if address is not None:
            company.address = address
        if postal_code is not None:
            company.postal_code = postal_code
        if phone is not None:
            company.phone = phone

        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def soft_delete(self, company: Company) -> Company:
        """사업장 Soft Delete"""
        company.is_deleted = True
        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def restore(self, company: Company) -> Company:
        """사업장 복구"""
        company.is_deleted = False
        await self.db.flush()
        await self.db.refresh(company)
        return company
