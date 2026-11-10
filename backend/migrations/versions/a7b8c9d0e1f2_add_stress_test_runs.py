"""add_stress_test_runs

Revision ID: a7b8c9d0e1f2
Revises: f3a4b5c6d7e8
Create Date: 2026-11-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'a7b8c9d0e1f2'
down_revision = 'f3a4b5c6d7e8'
branch_labels = None
depends_on = None


task_status_enum = postgresql.ENUM(
    'NONE', 'PENDING', 'DOWNLOADING', 'EVALUATING', 'COMPLETED', 'CANCELLED', 'FAILED',
    name='task_status_enum',
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        'stress_test_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('celery_task_id', sa.String(), nullable=True),
        sa.Column('status', task_status_enum, nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('results_dir', sa.String(), nullable=True),
        sa.Column('archive_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stress_test_runs_id'), 'stress_test_runs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_stress_test_runs_id'), table_name='stress_test_runs')
    op.drop_table('stress_test_runs')
