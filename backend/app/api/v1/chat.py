# Chat API 라우터 - AI 노동법 Q&A 챗봇
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate
from app.schemas.common import ApiResponse
from app.core.dependencies import get_current_user_id, get_current_company_id, get_redis
from app.core.rate_limit import check_rate_limit
from app.services.chat_service import ChatService

router = APIRouter()


@router.get(
    "/sessions",
    response_model=ApiResponse[list],
    summary="채팅 세션 목록",
    description="사용자의 채팅 세션 목록을 조회합니다.",
)
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    sessions = await service.list_sessions(user_id, skip=skip, limit=limit)
    return ApiResponse(success=True, data=sessions)


@router.post(
    "/sessions",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="새 채팅 세션 생성",
    description="새로운 채팅 세션을 생성합니다.",
)
async def create_session(
    request: ChatSessionCreate,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    session = await service.create_session(
        user_id=user_id,
        company_id=company_id,
        title=request.title,
    )
    return ApiResponse(success=True, data=session)


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[dict],
    summary="채팅 세션 상세",
    description="채팅 세션 정보와 메시지를 조회합니다.",
)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    detail = await service.get_session_detail(session_id, user_id)
    return ApiResponse(success=True, data=detail)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="채팅 세션 삭제",
    description="채팅 세션과 모든 메시지를 삭제합니다.",
)
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    await service.delete_session(session_id, user_id)


@router.post(
    "/sessions/{session_id}/messages",
    summary="메시지 전송 (SSE 스트리밍)",
    description="메시지를 전송하고 AI 응답을 SSE 스트리밍으로 받습니다.",
)
async def send_message(
    session_id: str,
    request: ChatMessageCreate,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    # Rate Limit 체크 (30회/시간)
    await check_rate_limit(
        redis=redis,
        key=f"ratelimit:chat:{user_id}",
        limit=30,
        window_seconds=3600,
    )

    service = ChatService(db, redis)

    return StreamingResponse(
        service.send_message(
            session_id=session_id,
            user_id=user_id,
            content=request.content,
            company_id=company_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/faq",
    response_model=ApiResponse[list],
    summary="자주 묻는 질문",
    description="자주 묻는 질문 카테고리 목록을 조회합니다.",
)
async def get_faq(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    faq = await service.get_faq()
    return ApiResponse(success=True, data=faq)
