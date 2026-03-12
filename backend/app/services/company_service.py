# 사업장 서비스
from typing import Optional, Any
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.db.models.company import Company
from app.repositories.company_repo import CompanyRepository
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.core.config import settings
from app.core.exceptions import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    ConflictError,
)


class CompanyService:
    """사업장 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession, redis: aioredis.Redis) -> None:
        self.db = db
        self.repo = CompanyRepository(db)
        self.redis = redis

    async def create_company(
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
    ) -> dict[str, Any]:
        """
        사업장 등록

        Args:
            owner_id: 소유자 ID
            business_name: 사업장명
            business_number: 사업자등록번호
            representative_name: 대표자명
            industry_type: 업종
            employee_count: 직원 수
            address: 주소
            postal_code: 우편번호
            phone: 전화번호

        Returns:
            생성된 사업장 정보

        Raises:
            ConflictError: 사업자등록번호 중복
        """
        # 사업자등록번호 중복 확인
        existing_company = await self.repo.get_by_business_number(business_number)
        if existing_company:
            raise ConflictError(
                message="이미 등록된 사업자등록번호입니다.",
                details=[{"field": "business_number", "message": "이미 사용 중인 사업자등록번호입니다."}]
            )

        # 사업장 생성
        company = await self.repo.create(
            owner_id=owner_id,
            business_name=business_name,
            business_number=business_number,
            representative_name=representative_name,
            industry_type=industry_type,
            employee_count=employee_count,
            address=address,
            postal_code=postal_code,
            phone=phone
        )

        await self.db.commit()

        return self._company_to_dict(company)

    async def get_companies(
        self,
        owner_id: uuid.UUID,
        limit: int = 20,
        cursor: Optional[str] = None,
        is_deleted: bool = False
    ) -> dict[str, Any]:
        """
        사업장 목록 조회

        Args:
            owner_id: 소유자 ID
            limit: 페이지 크기 (최대 100)
            cursor: 페이지네이션 커서
            is_deleted: 삭제된 사업장 포함 여부

        Returns:
            사업장 목록과 페이지네이션 정보
        """
        limit = min(limit, 100)  # 최대 100개 제한

        # TODO: 커서 기반 페이지네이션 구현 (현재는 offset 기반)
        skip = 0
        companies = await self.repo.list_by_owner(
            owner_id=owner_id,
            skip=skip,
            limit=limit,
            is_deleted=is_deleted
        )
        total_count = await self.repo.count_by_owner(owner_id, is_deleted=is_deleted)

        return {
            "data": [self._company_to_list_item(c) for c in companies],
            "pagination": {
                "cursor": None,  # TODO: 커서 기반 구현 시
                "hasNext": skip + limit < total_count,
                "limit": limit,
                "totalCount": total_count
            }
        }

    async def get_company(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> dict[str, Any]:
        """
        사업장 상세 조회

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)

        Returns:
            사업장 상세 정보

        Raises:
            NotFoundError: 사업장을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장 접근
        """
        company = await self.repo.get_by_id(company_id)

        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        # 소유권 확인
        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장에 접근할 수 없습니다.")

        return self._company_to_dict(company)

    async def update_company(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        business_name: Optional[str] = None,
        representative_name: Optional[str] = None,
        industry_type: Optional[str] = None,
        employee_count: Optional[int] = None,
        address: Optional[str] = None,
        postal_code: Optional[str] = None,
        phone: Optional[str] = None
    ) -> dict[str, Any]:
        """
        사업장 정보 수정

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)
            business_name: 사업장명
            representative_name: 대표자명
            industry_type: 업종
            employee_count: 직원 수
            address: 주소
            postal_code: 우편번호
            phone: 전화번호

        Returns:
            수정된 사업장 정보

        Raises:
            NotFoundError: 사업장을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장 수정
        """
        company = await self.repo.get_by_id(company_id)

        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        # 소유권 확인
        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장을 수정할 수 없습니다.")

        # 사업장 수정 (business_number는 수정 불가)
        company = await self.repo.update(
            company=company,
            business_name=business_name,
            representative_name=representative_name,
            industry_type=industry_type,
            employee_count=employee_count,
            address=address,
            postal_code=postal_code,
            phone=phone
        )

        await self.db.commit()

        return self._company_to_dict(company)

    async def delete_company(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        confirmation: str
    ) -> None:
        """
        사업장 삭제 (Soft Delete)

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID (권한 확인용)
            confirmation: 사업장명 확인

        Raises:
            NotFoundError: 사업장을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장 삭제
            ValidationError: 확인 문구 불일치
        """
        company = await self.repo.get_by_id(company_id)

        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        # 소유권 확인
        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장을 삭제할 수 없습니다.")

        # 확인 문구 검증
        if confirmation != company.business_name:
            raise ValidationError(
                message="확인 문구가 일치하지 않습니다.",
                details=[{"field": "confirmation", "message": "사업장명을 정확하게 입력해주세요."}]
            )

        # Soft Delete
        await self.repo.soft_delete(company)

        await self.db.commit()

    async def select_company(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        user_plan: str = "free",
        user_role: str = "owner"
    ) -> dict[str, Any]:
        """
        사업장 선택 (컨텍스트 변경)

        Args:
            company_id: 사업장 ID
            user_id: 요청 사용자 ID
            user_plan: 사용자 플랜
            user_role: 사용자 역할

        Returns:
            새 토큰과 사업장 정보

        Raises:
            NotFoundError: 사업장을 찾을 수 없음
            ForbiddenError: 다른 사용자의 사업장 선택
        """
        company = await self.repo.get_by_id(company_id)

        if company is None:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        # 소유권 확인
        if company.owner_id != user_id:
            raise ForbiddenError("다른 사용자의 사업장을 선택할 수 없습니다.")

        # 새 토큰 생성 (company_id 포함)
        access_token = create_access_token(
            user_id=str(user_id),
            company_id=str(company_id),
            plan=user_plan,
            role=user_role
        )

        refresh_token = create_refresh_token(str(user_id))

        # Refresh Token Redis 저장 (Rotation)
        token_value = refresh_token[3:]  # rt_ 접두사 제거
        await self.redis.setex(
            f"refresh:{user_id}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            token_value
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "company": self._company_to_list_item(company)
        }

    def _company_to_dict(self, company: Company) -> dict[str, Any]:
        """Company 모델을 딕셔너리로 변환"""
        return {
            "id": str(company.id),
            "owner_id": str(company.owner_id),
            "business_name": company.business_name,
            "business_number": company.business_number,
            "representative_name": company.representative_name,
            "industry_type": company.industry_type,
            "employee_count": company.employee_count,
            "address": company.address,
            "postal_code": company.postal_code,
            "phone": company.phone,
            "work_rule_required": company.work_rule_required,
            "created_at": company.created_at.isoformat(),
            "updated_at": company.updated_at.isoformat()
        }

    def _company_to_list_item(self, company: Company) -> dict[str, Any]:
        """Company 모델을 목록 아이템으로 변환"""
        return {
            "id": str(company.id),
            "business_name": company.business_name,
            "business_number": company.business_number,
            "representative_name": company.representative_name,
            "industry_type": company.industry_type,
            "employee_count": company.employee_count,
            "address": company.address,
            "postal_code": company.postal_code,
            "phone": company.phone,
            "work_rule_required": company.work_rule_required,
            "created_at": company.created_at.isoformat()
        }
