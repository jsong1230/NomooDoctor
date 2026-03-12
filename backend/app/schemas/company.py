# Company 관련 스키마
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
import uuid


class CompanyBase(BaseModel):
    """Company 기본 스키마"""
    business_name: str = Field(..., min_length=1, max_length=200, description="사업장명")
    business_number: str = Field(..., pattern=r"^\d{3}-\d{2}-\d{5}$", description="사업자등록번호 (xxx-xx-xxxxx)")
    representative_name: str = Field(..., min_length=1, max_length=100, description="대표자명")
    industry_type: Literal["manufacturing", "food_service", "retail", "service", "it", "construction", "healthcare", "other"] = Field(..., description="업종")
    employee_count: int = Field(..., ge=0, le=1000, description="직원 수")
    address: Optional[str] = Field(None, description="주소")
    postal_code: Optional[str] = Field(None, description="우편번호")
    phone: Optional[str] = Field(None, description="대표 전화번호")

    @field_validator("business_number")
    @classmethod
    def validate_business_number(cls, v: str) -> str:
        """사업자등록번호 형식 검증 (공백 제거)"""
        v = v.strip()
        return v


class CompanyCreate(CompanyBase):
    """Company 생성"""
    pass


class CompanyUpdate(BaseModel):
    """Company 수정"""
    business_name: Optional[str] = Field(None, min_length=1, max_length=200)
    representative_name: Optional[str] = Field(None, min_length=1, max_length=100)
    industry_type: Optional[Literal["manufacturing", "food_service", "retail", "service", "it", "construction", "healthcare", "other"]] = None
    employee_count: Optional[int] = Field(None, ge=0, le=1000)
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None


class CompanyDeleteRequest(BaseModel):
    """Company 삭제 요청"""
    confirmation: str = Field(..., description="사업장명 확인 (삭제 확인용)")


class CompanySelectRequest(BaseModel):
    """Company 선택 요청"""
    pass  # 빈 스키마


class CompanyResponse(CompanyBase):
    """Company 응답"""
    id: uuid.UUID
    owner_id: uuid.UUID
    work_rule_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyListItem(CompanyBase):
    """Company 목록 아이템"""
    id: uuid.UUID
    work_rule_required: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """페이지네이션 메타"""
    cursor: Optional[str] = Field(None, description="다음 페이지 커서")
    hasNext: bool = Field(..., description="다음 페이지 존재 여부")
    limit: int = Field(..., ge=1, le=100, description="페이지 크기")
    totalCount: int = Field(..., ge=0, description="전체 개수")


class CompanyListResponse(BaseModel):
    """Company 목록 응답"""
    data: list[CompanyListItem]
    pagination: PaginationMeta


class TokenResponse(BaseModel):
    """토큰 응답 (사업장 선택 시)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    company: CompanyListItem


class CompanySelectResponse(BaseModel):
    """사업장 선택 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    company: CompanyListItem
