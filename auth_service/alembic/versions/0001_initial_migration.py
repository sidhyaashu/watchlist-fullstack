"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2026-04-13 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('dob', sa.Date(), nullable=True),
        sa.Column('auth_provider', sa.Enum('LOCAL', 'GOOGLE', 'BOTH', name='authproviderenum'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='userstatusenum'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('failed_attempts', sa.Integer(), nullable=True),
        sa.Column('lock_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_ip', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('token_version', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('idx_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('idx_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('idx_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('idx_users_status'), 'users', ['status'], unique=False)

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('idx_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)

    # Create otp_codes table
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(), nullable=False),
        sa.Column('otp_type', sa.Enum('EMAIL_VERIFY', 'PASSWORD_RESET', 'SETUP_PASSWORD', name='otptypeenum'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('idx_otp_codes_id'), 'otp_codes', ['id'], unique=False)
    op.create_index('idx_otp_codes_user_id', 'otp_codes', ['user_id'], unique=False)

    # Create user_analytics table
    op.create_table(
        'user_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.Enum('LOGIN', 'LOGOUT', 'FAILED_LOGIN', 'REGISTER', 'PASSWORD_CHANGE', 'PROFILE_UPDATE', 'ACCOUNT_DELETE', name='analyticseventtypeenum'), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('idx_user_analytics_id'), 'user_analytics', ['id'], unique=False)
    op.create_index('idx_analytics_user_id', 'user_analytics', ['user_id'], unique=False)

    # Create user_daily_activity table
    op.create_table(
        'user_daily_activity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('login_count', sa.Integer(), nullable=True),
        sa.Column('profile_update_count', sa.Integer(), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('idx_user_daily_activity_id'), 'user_daily_activity', ['id'], unique=False)
    op.create_index('idx_daily_activity_date', 'user_daily_activity', ['activity_date'], unique=False)


def downgrade() -> None:
    op.drop_table('user_daily_activity')
    op.drop_table('user_analytics')
    op.drop_table('otp_codes')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    
    # Drop enums manually if needed (Postgres specific)
    op.execute('DROP TYPE authproviderenum')
    op.execute('DROP TYPE userstatusenum')
    op.execute('DROP TYPE otptypeenum')
    op.execute('DROP TYPE analyticseventtypeenum')
