"""pgvector 확장 및 law_vectors 테이블 추가

Revision ID: 003
Revises: 002
Create Date: 2026-03-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector 확장 활성화
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # law_vectors 테이블 생성
    op.create_table(
        "law_vectors",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("law_name", sa.String(100), nullable=False),
        sa.Column("article", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        # OpenAI text-embedding-ada-002 / text-embedding-3-small 차원: 1536
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("keywords", ARRAY(sa.Text), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # 벡터 유사도 검색용 IVFFlat 인덱스 (코사인 거리 기준)
    # lists=100: 데이터 수가 적을 때 적합한 설정 (권장: sqrt(행수))
    op.execute("""
        CREATE INDEX idx_law_vectors_embedding
        ON law_vectors
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    # 인덱스 삭제 (테이블 삭제 시 자동 삭제되지만 명시적으로 처리)
    op.execute("DROP INDEX IF EXISTS idx_law_vectors_embedding")

    # law_vectors 테이블 삭제
    op.drop_table("law_vectors")

    # pgvector 확장 삭제 (다른 테이블이 사용 중일 수 있으므로 주의)
    op.execute("DROP EXTENSION IF EXISTS vector")
