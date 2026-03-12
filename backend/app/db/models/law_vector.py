# LawVector 모델 — 법령 조항과 OpenAI 임베딩 벡터를 저장
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.base import Base
import uuid


class LawVector(Base):
    """법령 벡터 테이블

    근로기준법 등 노동 관련 법령의 조항을 저장하고,
    OpenAI 임베딩 벡터를 이용한 의미 유사도 검색을 지원한다.
    """

    __tablename__ = "law_vectors"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # 법령명 (예: 근로기준법, 최저임금법)
    law_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 조항 (예: 제50조, 제60조)
    article: Mapped[str] = mapped_column(String(50), nullable=False)
    # 조항 내용 (전문)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # OpenAI text-embedding-ada-002 기준 1536차원 벡터 (생성 전에는 null)
    embedding = mapped_column(Vector(1536), nullable=True)
    # 검색 및 분류용 키워드 배열
    keywords = mapped_column(ARRAY(Text), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
