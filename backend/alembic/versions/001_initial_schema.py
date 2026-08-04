"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-21 23:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. zones table
    op.create_table(
        'zones',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('polygon_coordinates', sa.Text(), nullable=False),
        sa.Column('site_location', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. gates table
    op.create_table(
        'gates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('camera_stream_url', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. equipment table
    op.create_table(
        'equipment',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('equipment_type', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('idle_duration_minutes', sa.Integer(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. violations table (audit table -> ON DELETE SET NULL)
    op.create_table(
        'violations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('gate_id', sa.UUID(), nullable=True),
        sa.Column('zone_id', sa.UUID(), nullable=True),
        sa.Column('worker_id', sa.UUID(), nullable=True),
        sa.Column('violation_type', sa.String(length=50), nullable=False),
        sa.Column('helmet_missing', sa.Boolean(), nullable=False),
        sa.Column('vest_missing', sa.Boolean(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['gate_id'], ['gates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['worker_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_violations_detected_at'), 'violations', ['detected_at'], unique=False)

    # 6. hazard_reports table (audit table -> ON DELETE SET NULL)
    op.create_table(
        'hazard_reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('reported_by', sa.UUID(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reported_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hazard_reports_category'), 'hazard_reports', ['category'], unique=False)

    # 7. delivery_logs table (audit table -> ON DELETE SET NULL, v2 material schema)
    op.create_table(
        'delivery_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('gate_id', sa.UUID(), nullable=True),
        sa.Column('reported_by', sa.UUID(), nullable=True),
        sa.Column('ai_vehicle_count', sa.Integer(), nullable=True),
        sa.Column('manual_reported_count', sa.Integer(), nullable=False),
        sa.Column('material_type', sa.String(length=50), nullable=False),
        sa.Column('material_quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantity_unit', sa.String(length=20), nullable=False),
        sa.Column('vehicle_type', sa.String(length=50), nullable=True),
        sa.Column('discrepancy_flag', sa.Boolean(), nullable=False),
        sa.Column('logged_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['gate_id'], ['gates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reported_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_delivery_logs_discrepancy_flag'), 'delivery_logs', ['discrepancy_flag'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_delivery_logs_discrepancy_flag'), table_name='delivery_logs')
    op.drop_table('delivery_logs')
    op.drop_index(op.f('ix_hazard_reports_category'), table_name='hazard_reports')
    op.drop_table('hazard_reports')
    op.drop_index(op.f('ix_violations_detected_at'), table_name='violations')
    op.drop_table('violations')
    op.drop_table('equipment')
    op.drop_table('gates')
    op.drop_table('zones')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
