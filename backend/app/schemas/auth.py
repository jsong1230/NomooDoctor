# 인증 관련 스키마
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None


class LoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class KakaoLoginRequest(BaseModel):
    """카카오 로그인 요청"""
    code: str


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str


class AuthUserResponse(BaseModel):
    """인증 응답 사용자 정보"""
    id: str
    email: str
    name: str
    phone: str | None
    role: str
    plan: str
    plan_expires_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class AuthResponse(BaseModel):
    """인증 응답"""
    user: AuthUserResponse
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
