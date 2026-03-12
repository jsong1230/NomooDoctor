"""add severance_records and termination_documents tables

Revision ID: 006
Revises: 005
Create Date: 2026-03-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # severance_records 테이블 생성
    op.create_table(
        'severance_records',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('resign_date', sa.Date(), nullable=False),
        sa.Column('total_service_days', sa.Integer(), nullable=False),
        sa.Column('last_3m_total_wage', sa.Numeric(14, 0), nullable=False),
        sa.Column('last_3m_total_days', sa.Integer(), nullable=False),
        sa.Column('bonus_3m_share', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('average_daily_wage', sa.Numeric(12, 0), nullable=False),
        sa.Column('severance_pay', sa.Numeric(14, 0), nullable=False),
        sa.Column('unused_leave_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unused_leave_pay', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('total_payment', sa.Numeric(14, 0), nullable=False),
        sa.Column('payment_deadline', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='calculated'),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calculation_detail', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('calculated', 'paid', 'overdue')", name="ck_severance_status"),
        sa.UniqueConstraint('employee_id', 'resign_date', name='uq_severance_employee_date'),
    )
    op.create_index('idx_severance_employee', 'severance_records', ['employee_id'])
    op.create_index('idx_severance_company', 'severance_records', ['company_id'])
    op.create_index('idx_severance_status', 'severance_records', ['status'], postgresql_where=sa.text("status != 'paid'"))

    # termination_documents 테이블 생성
    op.create_table(
        'termination_documents',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('document_type', sa.String(30), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('pdf_url', sa.Text(), nullable=True),
        sa.Column('docx_url', sa.Text(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.CheckConstraint("document_type IN ('dismissal_notice', 'resignation_agreement')", name="ck_termination_doc_type"),
    )
    op.create_index('idx_termination_docs_employee', 'termination_documents', ['employee_id'])
    op.create_index('idx_termination_docs_company', 'termination_documents', ['company_id'])


def downgrade() -> None:
    op.drop_index('idx_termination_docs_company')
    op.drop_index('idx_termination_docs_employee')
    op.drop_table('termination_documents')

    op.drop_index('idx_severance_status')
    op.drop_index('idx_severance_company')
    op.drop_index('idx_severance_employee')
    op.drop_table('severance_records')
