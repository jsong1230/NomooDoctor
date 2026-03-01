# Users API 라우터
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.user_service import UserService
from app.schemas.user import UserUpdate, ChangePasswordRequest, UserResponse
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_info(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    현재 사용자 정보 조회

    로그인한 사용자의 정보를 반환합니다.
    """
    user_service = UserService(db)
    result = await user_service.get_me(user)

    return ApiResponse(data=result)


@router.patch("/me", response_model=ApiResponse[UserResponse])
async def update_current_user_info(
    request: UserUpdate,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    현재 사용자 정보 수정

    로그인한 사용자의 정보를 수정합니다.
    """
    user_service = UserService(db)
    result = await user_service.update_me(user, name=request.name, phone=request.phone)

    return ApiResponse(data=result, meta={"message": "정보가 수정되었습니다."})


@router.post("/me/password", response_model=ApiResponse[dict])
async def change_password(
    request: ChangePasswordRequest,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    비밀번호 변경

    로그인한 사용자의 비밀번호를 변경합니다.
    """
    user_service = UserService(db)
    await user_service.change_password(
        user=user,
        current_password=request.current_password,
        new_password=request.new_password
    )

    return ApiResponse(data=None, meta={"message": "비밀번호가 변경되었습니다."})
