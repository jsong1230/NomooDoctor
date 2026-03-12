# 노무사 마켓플레이스 스키마
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


# ===== 노무사 프로필 =====
class AttorneyResponse(BaseModel):
    """노무사 응답"""
    id: UUID
    name: str
    firm_name: Optional[str]
    specialties: List[str]
    regions: List[str]
    consultation_fee: int
    experience_years: int
    rating: float
    review_count: int
    response_rate: int
    bio: Optional[str]
    profile_image_url: Optional[str]
    verified: bool


class AttorneyDetailResponse(BaseModel):
    """노무사 상세 응답"""
    attorney: AttorneyResponse
    recent_reviews: List["ReviewResponse"]


# ===== 상담 케이스 =====
class CreateCaseRequest(BaseModel):
    """상담 신청 요청"""
    attorney_id: UUID
    company_id: Optional[UUID] = None
    chat_session_id: Optional[UUID] = None
    case_type: str = Field(..., pattern=r"^(dismissal|wage|leave|industrial_accident|harassment|other)$")
    urgency: str = Field(..., pattern=r"^(low|medium|high|emergency)$")
    consultation_type: str = Field(default="video", pattern=r"^(video|phone|visit)$")
    preferred_schedule: Optional[List[str]] = None
    description: Optional[str] = None


class CaseResponse(BaseModel):
    """케이스 응답"""
    id: UUID
    attorney_id: UUID
    attorney_name: str
    case_summary: str
    case_type: str
    urgency: str
    status: str
    consultation_type: str
    consultation_fee: int
    scheduled_at: Optional[datetime]
    fee_paid: bool
    completed_at: Optional[datetime]
    created_at: datetime


class CaseCreateResult(BaseModel):
    """케이스 생성 결과"""
    case_id: UUID
    case_summary: str
    status: str
    consultation_fee: int


# ===== 리뷰 =====
class CreateReviewRequest(BaseModel):
    """리뷰 작성 요청"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """리뷰 응답"""
    id: UUID
    rating: int
    comment: Optional[str]
    user_name: str
    created_at: datetime


class ReviewCreateResult(BaseModel):
    """리뷰 생성 결과"""
    review_id: UUID


# ===== 페이지네이션 =====
class AttorneyListResponse(BaseModel):
    """노무사 목록 응답"""
    attorneys: List[AttorneyResponse]
    total_count: int


class CaseListResponse(BaseModel):
    """케이스 목록 응답"""
    cases: List[CaseResponse]
    total_count: int


class ReviewListResponse(BaseModel):
    """리뷰 목록 응답"""
    reviews: List[ReviewResponse]
    total_count: int


# Forward ref 해결
AttorneyDetailResponse.model_rebuild()
