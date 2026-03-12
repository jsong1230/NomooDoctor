# FastAPI 애플리케이션 진입점
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import (
    AppError,
    ValidationError,
    app_error_handler,
    validation_error_handler,
    request_validation_error_handler,
)
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행
    yield
    # 애플리케이션 종료 시 실행
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI 기반 노무/HR 자동화 SaaS API",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예외 핸들러 등록
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "nomoodoc-backend"}
