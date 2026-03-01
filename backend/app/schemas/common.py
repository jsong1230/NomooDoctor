# 공통 스키마
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    """공통 API 응답"""
    success: bool = True
    data: DataT | None = None
    meta: dict[str, Any] | None = None


class PaginationMeta(BaseModel):
    """페이지네이션 메타"""
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    total: int = Field(ge=0)


class PaginatedResponse(ApiResponse[list[DataT]], Generic[DataT]):
    """페이지네이션 응답"""
    meta: PaginationMeta


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: dict[str, Any]


class ErrorDetail(BaseModel):
    """에러 상세"""
    field: str | None = None
    message: str
