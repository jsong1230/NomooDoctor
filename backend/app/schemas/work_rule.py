# WorkRule 관련 스키마
from datetime import datetime, date
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


class WorkRuleSectionSchema(BaseModel):
    """취업규칙 섹션"""
    section_number: int = Field(..., ge=1, le=14)
    title: str = Field(..., min_length=1, max_length=200)
    content_html: str = Field(..., min_length=1)
    is_required: bool = True
    law_reference: Optional[str] = None


class WorkRuleContentSchema(BaseModel):
    """취업규칙 컨텐츠"""
    sections: list[WorkRuleSectionSchema]


class WorkRuleCreate(BaseModel):
    """취업규칙 생성 요청"""
    industry_type: Literal["manufacturing", "food_service", "service", "it"] = Field(...)
    effective_date: Optional[date] = None


class WorkRuleUpdate(BaseModel):
    """취업규칙 수정 요청"""
    content: Optional[WorkRuleContentSchema] = None
    effective_date: Optional[date] = None
    status: Optional[Literal["draft", "under_review", "active"]] = None
    worker_consent_count: Optional[int] = Field(None, ge=0)
    total_worker_count: Optional[int] = Field(None, ge=0)
    approval_date: Optional[date] = None


class WorkRuleGenerateRequest(BaseModel):
    """AI 초안 생성 요청"""
    industry_type: Optional[Literal["manufacturing", "food_service", "service", "it"]] = None
    additional_context: Optional[str] = Field(None, max_length=1000)


class WorkRuleReviseRequest(BaseModel):
    """개정 요청"""
    revision_reason: str = Field(..., min_length=1, max_length=500)
    effective_date: Optional[date] = None


class WorkRuleResponse(BaseModel):
    """취업규칙 응답"""
    id: uuid.UUID
    company_id: uuid.UUID
    version: int
    status: str
    industry_type: str
    content: dict
    effective_date: Optional[date] = None
    approval_date: Optional[date] = None
    worker_consent_count: Optional[int] = None
    total_worker_count: Optional[int] = None
    revision_reason: Optional[str] = None
    ai_generated: bool
    ai_model: Optional[str] = None
    docx_url: Optional[str] = None
    pdf_url: Optional[str] = None
    filed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkRuleListItem(BaseModel):
    """취업규칙 목록 아이템"""
    id: uuid.UUID
    version: int
    status: str
    industry_type: str
    effective_date: Optional[date] = None
    approval_date: Optional[date] = None
    worker_consent_count: Optional[int] = None
    ai_generated: bool
    filed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DownloadResponse(BaseModel):
    """다운로드 응답"""
    download_url: str
    filename: str
    expires_at: str


class ConsentChecklistStep(BaseModel):
    """동의 절차 체크리스트 단계"""
    step: int
    title: str
    description: str
    law_reference: str
    is_required: bool


class ConsentChecklistResponse(BaseModel):
    """동의 절차 체크리스트 응답"""
    checklist: list[ConsentChecklistStep]
    employee_count: int
    consent_threshold: int
    consent_type: str  # "majority" | "opinion"


class TemplateSection(BaseModel):
    """템플릿 섹션"""
    section_number: int
    title: str
    description: str


class TemplateResponse(BaseModel):
    """템플릿 응답"""
    industry_type: str
    industry_name: str
    description: str
    sections: list[TemplateSection]
