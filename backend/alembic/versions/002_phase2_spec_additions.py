"""phase2 spec additions

Revision ID: 002_phase2_spec_additions
Revises: 001_initial_schema
Create Date: 2026-07-24 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_phase2_spec_additions'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Add columns & foreign keys to violations table
    with op.batch_alter_table('violations') as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=50), server_default='pending', nullable=False))
        batch_op.add_column(sa.Column('acknowledged_by', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('acknowledged_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
        batch_op.create_foreign_key('fk_violations_acknowledged_by', 'users', ['acknowledged_by'], ['id'], ondelete='SET NULL')

    # 2. Add columns & foreign keys to delivery_logs table
    with op.batch_alter_table('delivery_logs') as batch_op:
        batch_op.add_column(sa.Column('discrepancy_resolved', sa.Boolean(), server_default='false', nullable=False))
        batch_op.add_column(sa.Column('resolved_by', sa.UUID(), nullable=True))
        batch_op.add_column(sa.Column('resolved_at', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('fk_delivery_logs_resolved_by', 'users', ['resolved_by'], ['id'], ondelete='SET NULL')

    # 3. Add columns & foreign keys to zones table
    with op.batch_alter_table('zones') as batch_op:
        batch_op.add_column(sa.Column('zone_type', sa.String(length=50), server_default='excavation', nullable=False))
        batch_op.add_column(sa.Column('polygon_coords', sa.Text(), server_default='[]', nullable=False))
        batch_op.add_column(sa.Column('camera_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('ppe_requirements', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
        batch_op.add_column(sa.Column('created_by', sa.UUID(), nullable=True))
        batch_op.create_foreign_key('fk_zones_created_by', 'users', ['created_by'], ['id'], ondelete='SET NULL')

    # 4. Add columns to equipment table
    with op.batch_alter_table('equipment') as batch_op:
        batch_op.add_column(sa.Column('identifier', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('location_description', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('idle_minutes', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('last_detected_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    # 5. Create gate_entries table
    op.create_table(
        'gate_entries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('gate_id', sa.UUID(), nullable=True),
        sa.Column('person_track_id', sa.Integer(), nullable=True),
        sa.Column('passed_ppe', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('helmet_present', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('vest_present', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('logged_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['gate_id'], ['gates.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Create admin_notifications table
    op.create_table(
        'admin_notifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=1000), nullable=False),
        sa.Column('severity', sa.String(length=50), server_default='high', nullable=False),
        sa.Column('gate_id', sa.UUID(), nullable=True),
        sa.Column('delivery_log_id', sa.UUID(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['gate_id'], ['gates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['delivery_log_id'], ['delivery_logs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    with op.batch_alter_table('equipment') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('last_detected_at')
        batch_op.drop_column('idle_minutes')
        batch_op.drop_column('location_description')
        batch_op.drop_column('identifier')

    with op.batch_alter_table('zones') as batch_op:
        batch_op.drop_constraint('fk_zones_created_by', type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('is_active')
        batch_op.drop_column('ppe_requirements')
        batch_op.drop_column('camera_id')
        batch_op.drop_column('polygon_coords')
        batch_op.drop_column('zone_type')

    with op.batch_alter_table('delivery_logs') as batch_op:
        batch_op.drop_constraint('fk_delivery_logs_resolved_by', type_='foreignkey')
        batch_op.drop_column('resolved_at')
        batch_op.drop_column('resolved_by')
        batch_op.drop_column('discrepancy_resolved')

    with op.batch_alter_table('violations') as batch_op:
        batch_op.drop_constraint('fk_violations_acknowledged_by', type_='foreignkey')
        batch_op.drop_column('notes')
        batch_op.drop_column('acknowledged_at')
        batch_op.drop_column('acknowledged_by')
        batch_op.drop_column('status')
