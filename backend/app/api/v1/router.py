"""API 라우터 집합"""
from fastapi import APIRouter

from app.api.v1 import auth, users, companies, employees, payroll, contracts, payslips, chat, compliance

# API 라우터 생성
api_router = APIRouter()

# 개별 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"])
api_router.include_router(companies.router, prefix="/companies", tags=["사업장"])
api_router.include_router(employees.router, prefix="/employees", tags=["직원"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["계약서"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["급여"])
api_router.include_router(payslips.router, prefix="/payslips", tags=["급여명세서"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI 챗봇"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["컴플라이언스"])
