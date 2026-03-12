"""F-13 근태 관리 스키마 변경

Revision ID: 005
Revises: 004
Create Date: 2026-03-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. work_records 테이블에 updated_at 컬럼 추가
    op.add_column('work_records',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 2. UNIQUE 인덱스 생성 (employee_id + work_date 중복 방지)
    op.create_index(
        'idx_work_records_unique_date',
        'work_records',
        ['employee_id', 'work_date'],
        unique=True
    )


def downgrade() -> None:
    # UNIQUE 인덱스 삭제
    op.drop_index('idx_work_records_unique_date', 'work_records')

    # updated_at 컬럼 삭제
    op.drop_column('work_records', 'updated_at')
