"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users 테이블
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('kakao_id', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='owner'),
        sa.Column('plan', sa.String(20), nullable=False, server_default='free'),
        sa.Column('plan_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_kakao_id', 'users', ['kakao_id'], unique=True)

    # companies 테이블
    op.create_table(
        'companies',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('business_name', sa.String(200), nullable=False),
        sa.Column('business_number', sa.String(20), nullable=False),
        sa.Column('representative_name', sa.String(100), nullable=False),
        sa.Column('industry_type', sa.String(50), nullable=False),
        sa.Column('employee_count', sa.Integer(), nullable=False, server_default=0),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('work_rule_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_companies_owner_id', 'companies', ['owner_id'])
    op.create_index('idx_companies_business_number', 'companies', ['business_number'], unique=True)

    # employees 테이블
    op.create_table(
        'employees',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('id_number', sa.String(20), nullable=True),
        sa.Column('nationality', sa.String(50), nullable=False, server_default='korean'),
        sa.Column('employment_type', sa.String(30), nullable=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('position', sa.String(100), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('resign_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('bank_name', sa.String(50), nullable=True),
        sa.Column('bank_account', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_employees_company_id', 'employees', ['company_id'])
    op.create_index('idx_employees_hire_date', 'employees', ['hire_date'])
    op.create_index('idx_employees_is_active', 'employees', ['company_id', 'is_active'])

    # contracts 테이블
    op.create_table(
        'contracts',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('contract_type', sa.String(30), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('work_location', sa.Text(), nullable=False),
        sa.Column('work_hours_per_week', sa.Numeric(4, 1), nullable=False),
        sa.Column('work_start_time', sa.Time(), nullable=False),
        sa.Column('work_end_time', sa.Time(), nullable=False),
        sa.Column('break_minutes', sa.Integer(), nullable=False, server_default=60),
        sa.Column('work_days', sa.String(20), nullable=False),
        sa.Column('wage_type', sa.String(20), nullable=False),
        sa.Column('base_wage', sa.Numeric(12, 0), nullable=False),
        sa.Column('meal_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('transport_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('probation_months', sa.Integer(), nullable=False, server_default=0),
        sa.Column('probation_wage_rate', sa.Numeric(3, 2), nullable=False, server_default=1.0),
        sa.Column('nda_included', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('non_compete_included', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('docx_url', sa.Text(), nullable=True),
        sa.Column('pdf_url', sa.Text(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default=True),
        sa.Column('ai_model', sa.String(50), nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sign_service_ref', sa.String(200), nullable=True),
        sa.Column('expiry_notice_30_sent', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('expiry_notice_7_sent', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
    )
    op.create_index('idx_contracts_employee_id', 'contracts', ['employee_id'])
    op.create_index('idx_contracts_company_id', 'contracts', ['company_id'])
    op.create_index('idx_contracts_end_date', 'contracts', ['end_date'])
    op.create_index('idx_contracts_status', 'contracts', ['status'])

    # salary_settings 테이블
    op.create_table(
        'salary_settings',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('wage_type', sa.String(20), nullable=False),
        sa.Column('base_wage', sa.Numeric(12, 0), nullable=False),
        sa.Column('meal_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('transport_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('income_tax_family_count', sa.Integer(), nullable=False, server_default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_salary_settings_employee', 'salary_settings', ['employee_id', 'effective_from'])

    # work_records 테이블
    op.create_table(
        'work_records',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('work_date', sa.Date(), nullable=False),
        sa.Column('scheduled_start', sa.Time(), nullable=False),
        sa.Column('scheduled_end', sa.Time(), nullable=False),
        sa.Column('actual_start', sa.Time(), nullable=True),
        sa.Column('actual_end', sa.Time(), nullable=True),
        sa.Column('break_minutes', sa.Integer(), nullable=False, server_default=60),
        sa.Column('overtime_minutes', sa.Integer(), nullable=False, server_default=0),
        sa.Column('night_minutes', sa.Integer(), nullable=False, server_default=0),
        sa.Column('holiday_minutes', sa.Integer(), nullable=False, server_default=0),
        sa.Column('is_holiday', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
    )
    op.create_index('idx_work_records_employee_date', 'work_records', ['employee_id', 'work_date'])
    op.create_index('idx_work_records_company_date', 'work_records', ['company_id', 'work_date'])

    # payslips 테이블
    op.create_table(
        'payslips',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('pay_year', sa.Integer(), nullable=False),
        sa.Column('pay_month', sa.Integer(), nullable=False),
        sa.Column('base_pay', sa.Numeric(12, 0), nullable=False),
        sa.Column('holiday_pay', sa.Numeric(12, 0), nullable=False, server_default=0),
        sa.Column('overtime_pay', sa.Numeric(12, 0), nullable=False, server_default=0),
        sa.Column('night_pay', sa.Numeric(12, 0), nullable=False, server_default=0),
        sa.Column('holiday_work_pay', sa.Numeric(12, 0), nullable=False, server_default=0),
        sa.Column('meal_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('transport_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('other_allowance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('gross_pay', sa.Numeric(12, 0), nullable=False),
        sa.Column('national_pension', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('health_insurance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('long_term_care', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('employment_insurance', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('income_tax', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('local_income_tax', sa.Numeric(10, 0), nullable=False, server_default=0),
        sa.Column('total_deduction', sa.Numeric(12, 0), nullable=False),
        sa.Column('net_pay', sa.Numeric(12, 0), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_via', sa.String(20), nullable=True),
        sa.Column('send_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('pdf_url', sa.Text(), nullable=True),
        sa.Column('calculation_detail', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
    )
    op.create_index('idx_payslips_unique', 'payslips', ['employee_id', 'pay_year', 'pay_month'], unique=True)
    op.create_index('idx_payslips_company_period', 'payslips', ['company_id', 'pay_year', 'pay_month'])

    # chat_sessions 테이블
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=False, server_default='low'),
        sa.Column('attorney_referred', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
    )
    op.create_index('idx_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    # chat_messages 테이블
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('law_references', postgresql.JSONB(), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('disclaimer_shown', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('model_used', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_chat_messages_session', 'chat_messages', ['session_id', 'created_at'])

    # work_rules 테이블
    op.create_table(
        'work_rules',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default=1),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('docx_url', sa.String(), nullable=True),
        sa.Column('pdf_url', sa.String(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('approval_date', sa.Date(), nullable=True),
        sa.Column('worker_consent_count', sa.Integer(), nullable=True),
        sa.Column('filed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    )

    # labor_attorneys 테이블
    op.create_table(
        'labor_attorneys',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('license_number', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('firm_name', sa.String(200), nullable=True),
        sa.Column('specialties', sa.Text(), nullable=False),
        sa.Column('regions', sa.Text(), nullable=False),
        sa.Column('consultation_fee', sa.Numeric(10, 0), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=True),
        sa.Column('rating', sa.Numeric(3, 2), nullable=False, server_default=0.00),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default=0),
        sa.Column('response_rate', sa.Numeric(5, 2), nullable=False, server_default=0.00),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('profile_image_url', sa.String(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_labor_attorneys_license', 'labor_attorneys', ['license_number'], unique=True)

    # attorney_cases 테이블
    op.create_table(
        'attorney_cases',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('attorney_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('case_summary', sa.Text(), nullable=False),
        sa.Column('case_type', sa.String(50), nullable=False),
        sa.Column('urgency', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('consultation_type', sa.String(20), nullable=True),
        sa.Column('fee_amount', sa.Numeric(10, 0), nullable=True),
        sa.Column('fee_paid', sa.Boolean(), nullable=False, server_default=False),
        sa.Column('fee_paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['attorney_id'], ['labor_attorneys.id']),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
    )

    # subscriptions 테이블
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('plan', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('toss_order_id', sa.String(100), nullable=True),
        sa.Column('toss_billing_key', sa.String(200), nullable=True),
        sa.Column('monthly_amount', sa.Numeric(10, 0), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('idx_subscriptions_expires', 'subscriptions', ['expires_at'])


def downgrade() -> None:
    op.drop_table('subscriptions')
    op.drop_table('attorney_cases')
    op.drop_table('labor_attorneys')
    op.drop_table('work_rules')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('payslips')
    op.drop_table('work_records')
    op.drop_table('salary_settings')
    op.drop_table('contracts')
    op.drop_table('employees')
    op.drop_table('companies')
    op.drop_table('users')
