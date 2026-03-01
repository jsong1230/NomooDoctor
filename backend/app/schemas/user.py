# User 관련 스키마
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserBase(BaseModel):
    """User 기본 스키마"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None


class UserCreate(UserBase):
    """User 생성"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User 수정"""
    name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = None


class UserResponse(UserBase):
    """User 응답"""
    id: uuid.UUID
    role: Literal["owner", "manager", "employee", "admin"]
    plan: Literal["free", "basic", "standard", "premium", "enterprise"]
    plan_expires_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
