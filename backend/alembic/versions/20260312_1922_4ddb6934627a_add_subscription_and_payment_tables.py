"""add_subscription_and_payment_tables

Revision ID: 4ddb6934627a
Revises: 006
Create Date: 2026-03-12 19:22:25.263787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ddb6934627a'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # subscriptions 테이블 생성
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('plan', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('toss_customer_key', sa.String(100), nullable=True),
        sa.Column('toss_billing_key', sa.String(200), nullable=True),
        sa.Column('toss_order_id', sa.String(100), nullable=True),
        sa.Column('monthly_amount', sa.Numeric(10, 0), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("plan IN ('free', 'basic', 'standard', 'premium')", name='chk_subscriptions_plan'),
        sa.CheckConstraint("status IN ('active', 'cancelled', 'expired', 'paused')", name='chk_subscriptions_status'),
    )

    # 인덱스 생성
    op.create_index('idx_subscriptions_user_status', 'subscriptions', ['user_id', 'status'])
    op.create_index('idx_subscriptions_expires_active', 'subscriptions', ['expires_at'], postgresql_where=sa.text('status = \'active\''))

    # payment_history 테이블 생성
    op.create_table(
        'payment_history',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('subscription_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('toss_payment_id', sa.String(100), nullable=True, unique=True),
        sa.Column('toss_order_id', sa.String(100), nullable=False),
        sa.Column('amount', sa.Numeric(10, 0), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('refund_amount', sa.Numeric(10, 0), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('pending', 'success', 'failed', 'refunded')", name='chk_payment_history_status'),
    )

    # 인덱스 생성
    op.create_index('idx_payment_history_user', 'payment_history', ['user_id', sa.text('created_at DESC')])
    op.create_index('idx_payment_history_subscription', 'payment_history', ['subscription_id'])
    op.create_index('idx_payment_history_toss_order', 'payment_history', ['toss_order_id'])

    # plan_usage 테이블 생성
    op.create_table(
        'plan_usage',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('usage_month', sa.Date(), nullable=False),
        sa.Column('chat_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('contract_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payslip_send_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attorney_consult_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'usage_month', name='uq_plan_usage_user_month'),
    )

    # 인덱스 생성
    op.create_index('idx_plan_usage_user_month', 'plan_usage', ['user_id', 'usage_month'], unique=True)

    # users 테이블에 plan_expires_at 컬럼 확인 및 추가 (이미 있을 경우 건너뜀)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'users'):
        raise Exception("users 테이블이 존재하지 않습니다")

    # users 테이블의 plan_expires_at 컬럼 확인
    inspector = sa.inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'plan_expires_at' not in columns:
        op.add_column('users', sa.Column('plan_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # users 테이블에서 plan_expires_at 컬럼 제거
    inspector = sa.inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'plan_expires_at' in columns:
        op.drop_column('users', 'plan_expires_at')

    # plan_usage 테이블 삭제
    op.drop_index('idx_plan_usage_user_month', table_name='plan_usage')
    op.drop_table('plan_usage')

    # payment_history 테이블 삭제
    op.drop_index('idx_payment_history_toss_order', table_name='payment_history')
    op.drop_index('idx_payment_history_subscription', table_name='payment_history')
    op.drop_index('idx_payment_history_user', table_name='payment_history')
    op.drop_table('payment_history')

    # subscriptions 테이블 삭제
    op.drop_index('idx_subscriptions_expires_active', table_name='subscriptions')
    op.drop_index('idx_subscriptions_user_status', table_name='subscriptions')
    op.drop_table('subscriptions')
