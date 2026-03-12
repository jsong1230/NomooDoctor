# Chat 관련 스키마
from typing import Literal
from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """채팅 세션 생성 요청"""
    title: str | None = Field(None, max_length=200, description="세션 제목")


class ChatSessionResponse(BaseModel):
    """채팅 세션 응답"""
    id: str
    title: str | None
    risk_level: str
    attorney_referred: bool
    message_count: int
    created_at: str
    updated_at: str


class ChatMessageCreate(BaseModel):
    """채팅 메시지 전송 요청"""
    content: str = Field(..., min_length=1, max_length=2000, description="메시지 내용")


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답"""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    law_references: dict | None = None
    risk_level: str | None = None
    disclaimer_shown: bool = False
    created_at: str


class ChatSessionDetailResponse(BaseModel):
    """세션 상세 응답 (메시지 포함)"""
    session: ChatSessionResponse
    messages: list[ChatMessageResponse]


class FAQItem(BaseModel):
    """자주 묻는 질문 항목"""
    category: str
    question: str
    description: str
