"""Add soft delete to companies table

Revision ID: 002
Revises: 001
Create Date: 2026-03-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = '001'


def upgrade() -> None:
    # 기존 인덱스 삭제 (조건부 인덱스를 위해)
    op.drop_index('idx_companies_business_number', table_name='companies')
    op.drop_index('idx_companies_owner_id', table_name='companies')

    # is_deleted 컬럼 추가
    op.add_column('companies', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))

    # 업종 체크 제약조건 추가
    op.create_check_constraint(
        'ck_company_industry_type',
        'companies',
        "industry_type IN ('manufacturing', 'food_service', 'retail', 'service', 'it', 'construction', 'healthcare', 'other')"
    )

    # work_rule_required 체크 제약조건 수정 (employee_count >= 10)
    # 기존 제약조건이 있으면 삭제 후 다시 생성
    op.execute("ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_work_rule_required_check")
    op.create_check_constraint(
        'ck_company_work_rule_required',
        'companies',
        "work_rule_required = (employee_count >= 10)"
    )

    # 조건부 인덱스 생성 (PostgreSQL 16 지원)
    op.execute("""
        CREATE INDEX idx_companies_owner_id_active
        ON companies(owner_id)
        WHERE is_deleted = FALSE
    """)

    op.execute("""
        CREATE UNIQUE INDEX idx_companies_business_number_active
        ON companies(business_number)
        WHERE is_deleted = FALSE
    """)

    op.execute("""
        CREATE INDEX idx_companies_is_deleted
        ON companies(is_deleted)
    """)


def downgrade() -> None:
    # 조건부 인덱스 삭제
    op.drop_index('idx_companies_is_deleted', table_name='companies')
    op.drop_index('idx_companies_business_number_active', table_name='companies')
    op.drop_index('idx_companies_owner_id_active', table_name='companies')

    # 체크 제약조건 삭제
    op.drop_constraint('ck_company_work_rule_required', 'companies', type_='check')
    op.drop_constraint('ck_company_industry_type', 'companies', type_='check')

    # is_deleted 컬럼 삭제
    op.drop_column('companies', 'is_deleted')

    # 기존 인덱스 복원
    op.create_index('idx_companies_owner_id', 'companies', ['owner_id'])
    op.create_index('idx_companies_business_number', 'companies', ['business_number'], unique=True)
