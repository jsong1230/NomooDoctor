# WorkRule API 라우터
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import uuid

from app.db.session import get_db
from app.schemas.work_rule import (
    WorkRuleCreate,
    WorkRuleUpdate,
    WorkRuleGenerateRequest,
    WorkRuleReviseRequest,
    WorkRuleResponse,
    DownloadResponse,
    ConsentChecklistResponse,
    TemplateResponse,
)
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.work_rule_service import WorkRuleService

router = APIRouter()


@router.get(
    "/templates",
    response_model=ApiResponse[list[TemplateResponse]],
    summary="업종별 템플릿 목록 조회",
    description="취업규칙 업종별 표준 템플릿을 조회합니다."
)
async def get_templates(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    industry_type: str | None = None,
):
    """업종별 템플릿 목록 조회"""
    service = WorkRuleService(db, redis)
    templates = service.get_templates(industry_type)
    return ApiResponse(data=templates)


@router.post(
    "/",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="취업규칙 초안 생성",
    description="취업규칙 초안을 생성합니다."
)
async def create_work_rule(
    request: WorkRuleCreate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """취업규칙 초안 생성"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:create_work_rule:{user_id}",
        limit=10,
        window_seconds=3600
    )

    service = WorkRuleService(db, redis)
    result = await service.create_work_rule(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        industry_type=request.industry_type,
        effective_date=request.effective_date
    )

    return ApiResponse(data=result, meta={"message": "취업규칙 초안이 생성되었습니다."})


@router.get(
    "/consent-checklist",
    response_model=ApiResponse[ConsentChecklistResponse],
    summary="동의 절차 체크리스트",
    description="근로자 과반수 동의 절차 체크리스트를 조회합니다."
)
async def get_consent_checklist(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """동의 절차 체크리스트 조회"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    from app.repositories.company_repo import CompanyRepository

    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    # 회사 정보 조회하여 직원 수 가져오기
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    employee_count = company.employee_count if company else 0

    service = WorkRuleService(db, redis)
    result = service.get_consent_checklist(employee_count)

    return ApiResponse(data=result)


@router.get(
    "/",
    response_model=ApiResponse[list],
    summary="취업규칙 목록 조회",
    description="취업규칙 목록을 조회합니다."
)
async def list_work_rules(
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
):
    """취업규칙 목록 조회"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:list_work_rules:{user_id}",
        limit=100,
        window_seconds=60
    )

    service = WorkRuleService(db, redis)
    skip = (page - 1) * per_page
    result = await service.get_work_rules(
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        status=status,
        limit=per_page,
        skip=skip
    )

    return ApiResponse(
        data=result["data"],
        meta={
            "pagination": result["pagination"]
        }
    )


@router.get(
    "/{work_rule_id}",
    response_model=ApiResponse[dict],
    summary="취업규칙 상세 조회",
    description="취업규칙 상세 정보를 조회합니다."
)
async def get_work_rule(
    work_rule_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """취업규칙 상세 조회"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    service = WorkRuleService(db, redis)
    result = await service.get_work_rule(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id)
    )

    return ApiResponse(data=result)


@router.put(
    "/{work_rule_id}",
    response_model=ApiResponse[dict],
    summary="취업규칙 수정",
    description="취업규칙을 수정합니다."
)
async def update_work_rule(
    work_rule_id: str,
    request: WorkRuleUpdate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """취업규칙 수정"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    service = WorkRuleService(db, redis)
    result = await service.update_work_rule(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        content=request.content.model_dump() if request.content else None,
        effective_date=request.effective_date,
        status=request.status,
        worker_consent_count=request.worker_consent_count,
        total_worker_count=request.total_worker_count,
        approval_date=request.approval_date
    )

    return ApiResponse(data=result, meta={"message": "취업규칙이 수정되었습니다."})


@router.delete(
    "/{work_rule_id}",
    response_model=ApiResponse[dict],
    summary="취업규칙 삭제",
    description="취업규칙을 삭제합니다."
)
async def delete_work_rule(
    work_rule_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """취업규칙 삭제"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    service = WorkRuleService(db, redis)
    await service.delete_work_rule(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id)
    )

    return ApiResponse(
        data=None,
        meta={"message": "취업규칙이 삭제되었습니다."}
    )


@router.post(
    "/{work_rule_id}/generate",
    response_model=ApiResponse[dict],
    summary="AI 초안 생성",
    description="Claude API로 AI 초안을 생성합니다."
)
async def generate_ai_draft(
    work_rule_id: str,
    request: WorkRuleGenerateRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """AI 초안 생성"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:generate_ai_draft:{user_id}",
        limit=5,
        window_seconds=3600
    )

    service = WorkRuleService(db, redis)
    result = await service.generate_ai_draft(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        industry_type=request.industry_type,
        additional_context=request.additional_context
    )

    return ApiResponse(data=result, meta={"message": "AI 초안이 생성되었습니다."})


@router.get(
    "/{work_rule_id}/download/{file_type}",
    response_model=ApiResponse[DownloadResponse],
    summary="다운로드",
    description="취업규칙을 Word/PDF로 다운로드합니다."
)
async def download_work_rule(
    work_rule_id: str,
    file_type: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """다운로드"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:download_work_rule:{user_id}",
        limit=20,
        window_seconds=3600
    )

    service = WorkRuleService(db, redis)
    result = await service.generate_download(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        file_type=file_type
    )

    return ApiResponse(data=result)


@router.post(
    "/{work_rule_id}/revise",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="개정",
    description="새 버전을 생성합니다 (개정)."
)
async def revise_work_rule(
    work_rule_id: str,
    request: WorkRuleReviseRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """개정"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    service = WorkRuleService(db, redis)
    result = await service.revise_work_rule(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        revision_reason=request.revision_reason,
        effective_date=request.effective_date
    )

    return ApiResponse(data=result, meta={"message": "새 버전이 생성되었습니다."})


@router.post(
    "/{work_rule_id}/file",
    response_model=ApiResponse[dict],
    summary="신고용 커버 서류 생성",
    description="고용노동부 신고용 커버 서류를 생성합니다."
)
async def generate_cover_document(
    work_rule_id: str,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """신고용 커버 서류 생성"""
    # 사업장 ID는 JWT payload에서 추출
    from app.core.security import decode_token
    auth_header = req.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    payload = decode_token(token)
    company_id = payload.get("company_id")

    if not company_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("사업장을 선택해주세요.")

    service = WorkRuleService(db, redis)
    result = await service.generate_cover_document(
        work_rule_id=uuid.UUID(work_rule_id),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id)
    )

    return ApiResponse(data=result)
