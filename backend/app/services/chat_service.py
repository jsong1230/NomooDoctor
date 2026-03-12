# Chat Service - AI 노동법 Q&A 챗봇 서비스
import json
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.config import settings
from app.repositories.chat_repo import ChatRepository
from app.db.models.chat import ChatSession, ChatMessage
from app.core.exceptions import NotFoundError
import uuid

logger = logging.getLogger(__name__)

# 면책 문구 (시스템 레벨 - 프롬프트 의존 금지)
DISCLAIMER = (
    "\n\n---\n"
    "**면책 고지**: 본 답변은 AI가 제공하는 일반적인 법률 정보이며, "
    "법적 조언이 아닙니다. 구체적인 사안에 대해서는 반드시 노무사 등 "
    "전문가의 상담을 받으시기 바랍니다."
)

# FAQ 카테고리
FAQ_CATEGORIES = [
    {"category": "임금", "question": "최저임금은 얼마인가요?",
     "description": "최저임금, 임금체불, 퇴직금 관련"},
    {"category": "근로시간", "question": "주 52시간제는 어떻게 적용되나요?",
     "description": "근로시간, 연장근로, 야간근로 관련"},
    {"category": "휴가", "question": "연차휴가는 어떻게 계산하나요?",
     "description": "연차, 생리휴가, 출산휴가 관련"},
    {"category": "해고", "question": "직원을 해고하려면 어떻게 해야 하나요?",
     "description": "해고 절차, 부당해고, 권고사직 관련"},
    {"category": "계약", "question": "근로계약서에 꼭 포함해야 할 내용은?",
     "description": "근로계약서, 수습기간, 계약직 관련"},
    {"category": "4대보험", "question": "4대보험 가입 기준이 어떻게 되나요?",
     "description": "국민연금, 건강보험, 고용보험, 산재보험 관련"},
    {"category": "산재", "question": "직원이 다치면 어떻게 처리하나요?",
     "description": "산업재해, 산재보험, 직업병 관련"},
]

SYSTEM_PROMPT = """당신은 '노무닥터'의 AI 노무 비서입니다. 대한민국 노동법에 기반하여 50인 미만 사업장의 사장님들께 정확하고 실용적인 답변을 제공합니다.

## 역할
- 대한민국 노동법 전문 AI 비서
- 50인 미만 사업장 맞춤형 답변
- 사장님(사업주) 관점에서 실행 가능한 조언

## 답변 규칙
1. 반드시 관련 법령 조항을 인용하세요 (예: 근로기준법 제50조)
2. 실제 적용 가능한 구체적인 조언을 제공하세요
3. 위반 시 과태료/벌금 정보가 있으면 함께 안내하세요
4. 불확실한 경우 "확실하지 않으므로 노무사 상담을 권장합니다"로 안내하세요
5. 답변은 간결하고 이해하기 쉽게 작성하세요

## 위험도 분류 기준
- LOW: 일반적인 정보 질문 (최저임금 금액, 연차 계산법 등)
- MEDIUM: 사업장 운영에 영향을 미치는 질문 (취업규칙, 근로시간 관리 등)
- HIGH: 법적 분쟁 가능성이 있는 질문 (해고, 임금체불, 차별 등)
- EMERGENCY: 즉각적인 법적 조치가 필요한 질문 (산업재해, 진정/고소, 노동위원회 등)

## 사업장 정보
{company_context}

## 관련 법령 참조
{law_context}"""


class ChatService:
    def __init__(self, db: AsyncSession, redis=None):
        self.db = db
        self.redis = redis
        self.repo = ChatRepository(db)

    async def create_session(
        self, user_id: str, company_id: str | None = None, title: str | None = None
    ) -> dict:
        session = await self.repo.create_session(
            user_id=uuid.UUID(user_id),
            company_id=uuid.UUID(company_id) if company_id else None,
            title=title,
        )
        await self.db.commit()
        return self._session_to_dict(session)

    async def get_session_detail(self, session_id: str, user_id: str) -> dict:
        session = await self.repo.get_session(
            uuid.UUID(session_id), uuid.UUID(user_id)
        )
        if not session:
            raise NotFoundError("채팅 세션을 찾을 수 없습니다.")
        messages = await self.repo.get_messages(uuid.UUID(session_id))
        return {
            "session": self._session_to_dict(session),
            "messages": [self._message_to_dict(m) for m in messages],
        }

    async def list_sessions(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[dict]:
        sessions = await self.repo.list_sessions(
            uuid.UUID(user_id), skip=skip, limit=limit
        )
        return [self._session_to_dict(s) for s in sessions]

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        result = await self.repo.delete_session(
            uuid.UUID(session_id), uuid.UUID(user_id)
        )
        if not result:
            raise NotFoundError("채팅 세션을 찾을 수 없습니다.")
        await self.db.commit()
        return True

    async def send_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        company_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """메시지 전송 및 AI 응답 스트리밍 (SSE)"""
        session = await self.repo.get_session(
            uuid.UUID(session_id), uuid.UUID(user_id)
        )
        if not session:
            raise NotFoundError("채팅 세션을 찾을 수 없습니다.")

        # 최대 20턴 체크 (user + assistant = 40 messages)
        if session.message_count >= 40:
            yield self._sse_event("error", {
                "code": "E-6001",
                "message": "대화 턴 수를 초과했습니다. 새 세션을 시작해주세요.",
            })
            return

        # 사용자 메시지 저장
        await self.repo.add_message(
            session_id=uuid.UUID(session_id),
            role="user",
            content=content,
        )
        await self.db.commit()

        # 대화 히스토리 조회 (최대 10턴 = 20메시지)
        history = await self.repo.get_messages(uuid.UUID(session_id), limit=20)

        # RAG: 관련 법령 벡터 검색
        law_context = await self._search_law_vectors(content)

        # 사업장 컨텍스트 구성
        company_context = await self._get_company_context(company_id)

        # Claude API 스트리밍 호출
        try:
            full_response = ""
            law_references: list[dict] = []
            risk_level = "low"

            async for event in self._stream_claude_response(
                history, law_context, company_context
            ):
                event_type = event.get("type")
                if event_type == "content":
                    full_response += event["text"]
                    yield self._sse_event("message", {"content": event["text"]})
                elif event_type == "risk_level":
                    risk_level = event["level"]

            # 면책 문구 추가 (100% 삽입률 필수)
            full_response += DISCLAIMER
            yield self._sse_event("message", {"content": DISCLAIMER})

            # 위험도 이벤트 전송
            yield self._sse_event("risk_level", {"level": risk_level.upper()})

            # AI 응답 저장
            assistant_message = await self.repo.add_message(
                session_id=uuid.UUID(session_id),
                role="assistant",
                content=full_response,
                law_references={"references": law_references} if law_references else None,
                risk_level=risk_level,
                disclaimer_shown=True,
                model_used=settings.ANTHROPIC_MODEL,
            )
            await self.db.commit()

            # 위험도 HIGH/EMERGENCY -> 노무사 연결 CTA
            if risk_level in ("high", "emergency"):
                await self.repo.update_session_attorney_referred(uuid.UUID(session_id))
                await self.db.commit()

            yield self._sse_event("done", {
                "message_id": str(assistant_message.id),
                "risk_level": risk_level.upper(),
                "attorney_referred": risk_level in ("high", "emergency"),
            })

        except Exception as e:
            logger.error(f"AI 응답 생성 오류: {e}")
            yield self._sse_event("error", {
                "code": "E-6003",
                "message": "답변 생성 중 오류가 발생했습니다.",
            })

    async def get_faq(self) -> list[dict]:
        return FAQ_CATEGORIES

    # --- 내부 메서드 ---

    async def _search_law_vectors(self, query: str) -> str:
        """pgvector 법령 검색 (임베딩 미생성 시 키워드 폴백)"""
        try:
            keywords = self._extract_keywords(query)
            if not keywords:
                return "관련 법령 정보가 없습니다."

            # 키워드 배열과 겹치는 법령 조회 (파라미터 바인딩)
            conditions = []
            params = {}
            for i, kw in enumerate(keywords):
                param_name = f"kw_{i}"
                conditions.append(f":{param_name} = ANY(keywords)")
                params[param_name] = kw

            where_clause = " OR ".join(conditions)
            sql = text(f"SELECT law_name, article, content FROM law_vectors WHERE {where_clause} LIMIT 3")
            result = await self.db.execute(sql, params)
            rows = result.fetchall()

            if not rows:
                return "관련 법령 정보가 없습니다."

            parts = []
            for row in rows:
                parts.append(f"[{row.law_name} {row.article}]\n{row.content}")
            return "\n\n".join(parts)

        except Exception as e:
            logger.warning(f"법령 벡터 검색 실패 (폴백): {e}")
            return "관련 법령 정보가 없습니다."

    def _extract_keywords(self, query: str) -> list[str]:
        """질문에서 노동법 관련 키워드 추출"""
        keyword_map = {
            "최저임금": ["최저임금", "임금"],
            "임금": ["임금", "급여"],
            "급여": ["임금", "급여"],
            "해고": ["해고", "부당해고"],
            "퇴직": ["퇴직", "퇴직금"],
            "퇴직금": ["퇴직금", "퇴직"],
            "연차": ["연차", "휴가"],
            "휴가": ["연차", "휴가"],
            "근로시간": ["근로시간", "연장근로"],
            "연장근로": ["연장근로", "근로시간"],
            "야간": ["야간근로", "근로시간"],
            "주휴": ["주휴수당", "임금"],
            "4대보험": ["4대보험", "국민연금", "건강보험"],
            "국민연금": ["국민연금", "4대보험"],
            "건강보험": ["건강보험", "4대보험"],
            "고용보험": ["고용보험", "4대보험"],
            "산재": ["산재보험", "산업재해"],
            "산업재해": ["산업재해", "산재보험"],
            "계약": ["근로계약", "계약"],
            "근로계약": ["근로계약", "계약"],
            "수습": ["수습", "근로계약"],
            "취업규칙": ["취업규칙"],
            "과태료": ["과태료", "벌금"],
        }
        found: set[str] = set()
        for trigger, kws in keyword_map.items():
            if trigger in query:
                found.update(kws)
        return list(found)[:5]

    async def _get_company_context(self, company_id: str | None) -> str:
        """사업장 컨텍스트 구성"""
        if not company_id:
            return "사업장 정보가 설정되지 않았습니다."
        try:
            from app.db.models.company import Company
            stmt = select(Company).where(Company.id == uuid.UUID(company_id))
            result = await self.db.execute(stmt)
            company = result.scalar_one_or_none()
            if not company:
                return "사업장 정보를 찾을 수 없습니다."
            return (
                f"- 사업장명: {company.business_name}\n"
                f"- 업종: {company.industry_type}\n"
                f"- 직원 수: {company.employee_count}명\n"
                f"- 취업규칙 의무: {'해당' if company.employee_count >= 10 else '비해당'}"
            )
        except Exception:
            return "사업장 정보 조회 중 오류가 발생했습니다."

    async def _stream_claude_response(
        self,
        history: list[ChatMessage],
        law_context: str,
        company_context: str,
    ) -> AsyncGenerator[dict, None]:
        """Claude API 스트리밍 호출"""
        system_prompt = SYSTEM_PROMPT.format(
            company_context=company_context,
            law_context=law_context,
        )

        # 대화 히스토리를 Claude 메시지 포맷으로 변환 (각 메시지 2000자 트림)
        messages = []
        for msg in history:
            if msg.role in ("user", "assistant"):
                content = msg.content[:2000] if len(msg.content) > 2000 else msg.content
                messages.append({"role": msg.role, "content": content})

        # API 키 미설정 시 Mock 모드
        if not settings.ANTHROPIC_API_KEY:
            yield {"type": "content", "text": "현재 AI 서비스가 설정되지 않았습니다. "}
            yield {"type": "content", "text": "ANTHROPIC_API_KEY를 설정해주세요."}
            yield {"type": "risk_level", "level": "low"}
            return

        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        try:
            async with client.messages.stream(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for chunk in stream.text_stream:
                    yield {"type": "content", "text": chunk}

            # 사용자 질문 기반 위험도 분류
            user_text = " ".join(
                msg["content"] for msg in messages if msg["role"] == "user"
            )
            risk_level = self._classify_risk(user_text)
            yield {"type": "risk_level", "level": risk_level}

        except Exception as e:
            logger.error(f"Claude API 오류: {e}")
            yield {"type": "content", "text": "AI 서비스에 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}
            yield {"type": "risk_level", "level": "low"}

    def _classify_risk(self, user_query: str) -> str:
        """질문 기반 위험도 분류"""
        emergency_keywords = ["산업재해", "산재", "고소", "진정", "노동위원회", "근로감독", "진정서"]
        high_keywords = ["해고", "부당해고", "임금체불", "차별", "성희롱", "직장내 괴롭힘", "권고사직"]
        medium_keywords = ["취업규칙", "근로시간", "52시간", "연장근로", "계약갱신"]

        for kw in emergency_keywords:
            if kw in user_query:
                return "emergency"
        for kw in high_keywords:
            if kw in user_query:
                return "high"
        for kw in medium_keywords:
            if kw in user_query:
                return "medium"
        return "low"

    @staticmethod
    def _sse_event(event_type: str, data: dict) -> str:
        """SSE 이벤트 포맷"""
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    def _session_to_dict(session: ChatSession) -> dict:
        return {
            "id": str(session.id),
            "title": session.title,
            "risk_level": session.risk_level,
            "attorney_referred": session.attorney_referred,
            "message_count": session.message_count,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        }

    @staticmethod
    def _message_to_dict(message: ChatMessage) -> dict:
        return {
            "id": str(message.id),
            "role": message.role,
            "content": message.content,
            "law_references": message.law_references,
            "risk_level": message.risk_level,
            "disclaimer_shown": message.disclaimer_shown,
            "created_at": message.created_at.isoformat(),
        }
