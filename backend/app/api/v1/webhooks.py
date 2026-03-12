# Webhook API Router
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.schemas.subscription import TossWebhookPayload
from app.services.payment_service import PaymentService
from app.services.contract_service import ContractService
from app.core.config import settings
import hmac
import hashlib
import json


router = APIRouter(prefix="/webhooks", tags=["토스 웹훅"])


@router.post("/toss")
async def toss_webhook(
    payload: TossWebhookPayload,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """토스페이먼츠 웹훅 수신"""
    # 서명 검증
    signature = request.headers.get("X-Toss-Signature", "")
    if not verify_toss_webhook_signature(payload.model_dump(), signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="서명이 올바르지 않습니다."
        )

    # 웹훅 처리
    service = PaymentService(db)
    await service.process_webhook(payload.eventType, payload.data)

    return {"status": "ok"}


def verify_toss_webhook_signature(payload: dict, signature: str) -> bool:
    """
    토스페이먼츠 웹훅 서명 검증

    Args:
        payload: 웹훅 페이로드 (dict)
        signature: X-Toss-Signature 헤더 값

    Returns:
        검증 성공 여부
    """
    if not settings.TOSS_SECRET_KEY:
        # Mock 모드: 검증 성공으로 간주
        return True

    # 페이로드를 문자열로 변환
    payload_str = json.dumps(payload, separators=(',', ':'))
    payload_bytes = payload_str.encode('utf-8')

    # HMAC-SHA256 생성
    expected = hmac.new(
        settings.TOSS_SECRET_KEY.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    # 서명 검증
    return hmac.compare_digest(expected, signature)


# === 모두싸인 웹훅 ===

class ModusignWebhookPayload(BaseModel):
    event: str
    document_id: str
    completed_at: str | None = None


@router.post("/modusign")
async def modusign_webhook(
    payload: ModusignWebhookPayload,
    db: AsyncSession = Depends(get_db),
):
    """모두싸인 전자서명 웹훅 수신"""
    if payload.event != "document.completed":
        return {"status": "ignored"}

    service = ContractService(db, None)
    handled = await service.handle_sign_webhook(
        document_id=payload.document_id,
        completed_at=payload.completed_at,
    )

    if not handled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 문서를 찾을 수 없습니다."
        )

    return {"status": "ok"}
