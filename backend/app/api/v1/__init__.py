# API v1 패키지
from fastapi import APIRouter

from app.api.v1 import auth, users, companies, employees

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"])
api_router.include_router(companies.router, prefix="/companies", tags=["사업장"])
api_router.include_router(employees.router, prefix="/employees", tags=["직원"])
