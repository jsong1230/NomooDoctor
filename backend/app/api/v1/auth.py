# 인증 API 라우터
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user_id, get_redis, get_request_ip
from app.core.rate_limit import check_rate_limit
from app.core.security import decode_token
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    KakaoLoginRequest,
    RefreshTokenRequest,
    AuthResponse,
    TokenResponse,
)
from app.schemas.common import ApiResponse

router = APIRouter()


@router.post("/register", response_model=ApiResponse[AuthResponse], status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    회원가입

    이메일, 비밀번호, 이름으로 새 사용자를 생성합니다.
    """
    # Rate Limit 체크 (3회/시간)
    client_ip = get_request_ip(req)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:register:{client_ip}",
        limit=3,
        window_seconds=3600
    )

    # 비밀번호 정책 검증 (영문 대소문자, 숫자, 특수문자 중 3가지 이상)
    password = request.password
    complexity_count = 0
    if any(c.isupper() for c in password):
        complexity_count += 1
    if any(c.islower() for c in password):
        complexity_count += 1
    if any(c.isdigit() for c in password):
        complexity_count += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        complexity_count += 1

    if complexity_count < 3:
        from app.core.exceptions import ValidationError
        raise ValidationError(
            message="비밀번호는 영문 대소문자, 숫자, 특수문자 중 3가지 이상을 조합해야 합니다.",
            details=[{"field": "password", "message": "비밀번호 복잡성 요건을 충족하지 않습니다."}]
        )

    # 회원가입 처리
    auth_service = AuthService(db, redis)
    result = await auth_service.register(
        email=request.email,
        password=request.password,
        name=request.name,
        phone=request.phone
    )

    return ApiResponse(data=result, meta={"message": "회원가입이 완료되었습니다."})


@router.post("/login", response_model=ApiResponse[AuthResponse])
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    로그인

    이메일과 비밀번호로 로그인합니다.
    """
    # Rate Limit 체크 (5회/분)
    client_ip = get_request_ip(req)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:login:{client_ip}",
        limit=5,
        window_seconds=60
    )

    # 로그인 처리
    auth_service = AuthService(db, redis)
    result = await auth_service.login(email=request.email, password=request.password)

    return ApiResponse(data=result, meta={"message": "로그인되었습니다."})


@router.post("/kakao")
async def kakao_login(
    request: KakaoLoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    카카오 로그인 시작

    카카오 인증 페이지로 리다이렉트합니다.
    """
    # TODO: 카카오 OAuth 구현 필요
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="카카오 로그인은 아직 구현되지 않았습니다."
    )


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    토큰 갱신

    Refresh Token으로 새 Access Token을 발급합니다.
    """
    # 토큰 갱신 처리
    auth_service = AuthService(db, redis)
    result = await auth_service.refresh(refresh_token=request.refresh_token)

    return ApiResponse(data=result)


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    로그아웃

    현재 세션을 종료합니다.
    """
    # Authorization 헤더에서 토큰 추출
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    # 토큰 디코딩하여 jti 추출
    try:
        payload = decode_token(token)
        token_jti = payload.get("jti", "")
    except Exception:
        token_jti = ""

    # 로그아웃 처리
    auth_service = AuthService(db, redis)
    await auth_service.logout(user_id=user_id, token_jti=token_jti)

    return ApiResponse(data=None, meta={"message": "로그아웃되었습니다."})
