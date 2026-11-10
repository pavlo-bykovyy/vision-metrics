"""add_attack_visualizations_and_charts_m2m

Revision ID: f3a4b5c6d7e8
Revises: e5955a16e356
Create Date: 2026-10-20 19:16:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f3a4b5c6d7e8'
down_revision = 'e5955a16e356'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'attack_visualization_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('exclude_russian', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('summary_payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_attack_visualization_runs_id'),
        'attack_visualization_runs',
        ['id'],
        unique=False,
    )

    op.create_table(
        'attack_charts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('visualization_run_id', sa.Integer(), nullable=True),
        sa.Column('chart_type', sa.String(length=80), nullable=False),
        sa.Column('task_scope', sa.String(length=80), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('subtitle', sa.Text(), nullable=True),
        sa.Column('chart_data', sa.JSON(), nullable=False),
        sa.Column('svg_content', sa.Text(), nullable=True),
        sa.Column('artifact_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['artifact_id'], ['artifacts.id']),
        sa.ForeignKeyConstraint(['visualization_run_id'], ['attack_visualization_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attack_charts_id'), 'attack_charts', ['id'], unique=False)
    op.create_index(op.f('ix_attack_charts_visualization_run_id'), 'attack_charts', ['visualization_run_id'], unique=False)
    op.create_index(op.f('ix_attack_charts_chart_type'), 'attack_charts', ['chart_type'], unique=False)
    op.create_index(op.f('ix_attack_charts_task_scope'), 'attack_charts', ['task_scope'], unique=False)

    op.create_table(
        'attack_visualization_run_tasks',
        sa.Column('visualization_run_id', sa.Integer(), nullable=False),
        sa.Column('evaluation_task_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_task_id'], ['evaluation_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['visualization_run_id'], ['attack_visualization_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('visualization_run_id', 'evaluation_task_id'),
    )

    op.create_table(
        'attack_chart_tasks',
        sa.Column('chart_id', sa.Integer(), nullable=False),
        sa.Column('evaluation_task_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chart_id'], ['attack_charts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evaluation_task_id'], ['evaluation_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chart_id', 'evaluation_task_id'),
    )

    op.create_table(
        'attack_chart_judge_runs',
        sa.Column('chart_id', sa.Integer(), nullable=False),
        sa.Column('judge_task_run_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chart_id'], ['attack_charts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['judge_task_run_id'], ['judge_task_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chart_id', 'judge_task_run_id'),
    )


def downgrade() -> None:
    op.drop_table('attack_chart_judge_runs')
    op.drop_table('attack_chart_tasks')
    op.drop_table('attack_visualization_run_tasks')
    op.drop_index(op.f('ix_attack_charts_task_scope'), table_name='attack_charts')
    op.drop_index(op.f('ix_attack_charts_chart_type'), table_name='attack_charts')
    op.drop_index(op.f('ix_attack_charts_visualization_run_id'), table_name='attack_charts')
    op.drop_index(op.f('ix_attack_charts_id'), table_name='attack_charts')
    op.drop_table('attack_charts')
    op.drop_index(op.f('ix_attack_visualization_runs_id'), table_name='attack_visualization_runs')
    op.drop_table('attack_visualization_runs')
