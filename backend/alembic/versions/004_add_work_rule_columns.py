"""Add work rule columns for F-08

Revision ID: 004
Revises: 003
Create Date: 2026-03-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 컬럼 추가
    op.add_column('work_rules', sa.Column('industry_type', sa.String(50), nullable=False, server_default='other'))
    op.add_column('work_rules', sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('work_rules', sa.Column('ai_model', sa.String(50), nullable=True))
    op.add_column('work_rules', sa.Column('revision_reason', sa.Text(), nullable=True))
    op.add_column('work_rules', sa.Column('total_worker_count', sa.Integer(), nullable=True))
    op.add_column('work_rules', sa.Column('cover_docx_url', sa.Text(), nullable=True))

    # 인덱스 생성
    op.create_index('idx_work_rules_company_version', 'work_rules', ['company_id', 'version'])
    op.create_index('idx_work_rules_company_status', 'work_rules', ['company_id', 'status'])


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('idx_work_rules_company_status')
    op.drop_index('idx_work_rules_company_version')

    # 컬럼 삭제
    op.drop_column('work_rules', 'cover_docx_url')
    op.drop_column('work_rules', 'total_worker_count')
    op.drop_column('work_rules', 'revision_reason')
    op.drop_column('work_rules', 'ai_model')
    op.drop_column('work_rules', 'ai_generated')
    op.drop_column('work_rules', 'industry_type')
