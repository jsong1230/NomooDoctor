# 커스텀 예외 클래스
from typing import Any
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class AppError(Exception):
    """애플리케이션 기본 예외"""

    def __init__(
        self,
        message: str,
        code: str = "E-9001",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: list[Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(AppError):
    """입력값 검증 오류 (E-1xxx)"""

    def __init__(self, message: str, details: list[Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="E-1001",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedError(AppError):
    """인증 오류 (E-2xxx)"""

    def __init__(self, message: str = "인증이 필요합니다.") -> None:
        super().__init__(
            message=message,
            code="E-2001",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(AppError):
    """권한 오류 (E-2xxx)"""

    def __init__(self, message: str = "접근 권한이 없습니다.") -> None:
        super().__init__(
            message=message,
            code="E-2005",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class PlanUpgradeRequiredError(AppError):
    """플랜 업그레이드 필요"""

    def __init__(self, required_plan: str) -> None:
        super().__init__(
            message=f"이 기능을 사용하려면 {required_plan} 플랜이 필요합니다.",
            code="E-7001",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundError(AppError):
    """리소스 없음 오류 (E-3xxx)"""

    def __init__(self, message: str = "요청한 리소스를 찾을 수 없습니다.") -> None:
        super().__init__(
            message=message,
            code="E-3002",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class RateLimitExceededError(AppError):
    """요청 한도 초과 (E-2xxx)"""

    def __init__(self, message: str = "요청 한도를 초과했습니다.") -> None:
        super().__init__(
            message=message,
            code="E-2006",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ConflictError(AppError):
    """리소스 충돌 오류 (E-3xxx)"""

    def __init__(self, message: str = "리소스 충돌이 발생했습니다.", details: list[Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="E-3001",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class BusinessNumberConflictError(ConflictError):
    """사업자등록번호 중복 오류 (E-4002)"""

    def __init__(self, message: str = "이미 등록된 사업자등록번호입니다.") -> None:
        super().__init__(
            message=message,
            code="E-4002",
        )


class BusinessNumberFormatError(ValidationError):
    """사업자등록번호 형식 오류 (E-4003)"""

    def __init__(self, message: str = "사업자등록번호 형식이 올바르지 않습니다.") -> None:
        super().__init__(
            message=message,
            code="E-4003",
        )


class CompanyNotFoundError(NotFoundError):
    """사업장 찾기 실패 (E-4001)"""

    def __init__(self, message: str = "사업장을 찾을 수 없습니다.") -> None:
        super().__init__(
            message=message,
            code="E-4001",
        )


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    success: bool = False
    error: dict[str, Any]


async def app_error_handler(request: Any, exc: AppError) -> JSONResponse:
    """AppError 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        ).model_dump(),
    )


async def validation_error_handler(request: Any, exc: ValidationError) -> JSONResponse:
    """ValidationError 핸들러"""
    return await app_error_handler(request, exc)


# ValidationException 임포트 (FastAPI 내부)
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError


# FastAPI RequestValidationError 변환
async def request_validation_error_handler(
    request: Any, exc: RequestValidationError
) -> JSONResponse:
    # 필수 필드 누락 확인
    for err in exc.errors():
        if err["type"] == "missing":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    error={
                        "code": "E-1003",
                        "message": "필수 필드가 누락되었습니다.",
                        "details": [
                            {"field": " -> ".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
                            for err in exc.errors()
                        ],
                    }
                ).model_dump(),
            )

    details = [
        {"field": " -> ".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error={
                "code": "E-1001",
                "message": "입력값을 확인해주세요.",
                "details": details,
            }
        ).model_dump(),
    )


# Pydantic ValidationError 변환 (서비스 레이어 등에서 발생)
validation_error_handler = request_validation_error_handler
