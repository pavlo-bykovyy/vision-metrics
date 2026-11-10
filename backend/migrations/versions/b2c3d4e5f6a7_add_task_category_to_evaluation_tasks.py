"""add_task_category_to_evaluation_tasks

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-20 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    task_category_enum = sa.Enum(
        'STANDARD', 'ATTACK',
        name='task_category_enum'
    )
    task_category_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'evaluation_tasks',
        sa.Column(
            'task_category',
            task_category_enum,
            nullable=False,
            server_default='STANDARD',
        )
    )
    op.create_index(
        op.f('ix_evaluation_tasks_task_category'),
        'evaluation_tasks',
        ['task_category'],
        unique=False,
    )

    op.execute(
        "UPDATE evaluation_tasks SET task_category = 'ATTACK' WHERE name LIKE 'attack:%'"
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_evaluation_tasks_task_category'), table_name='evaluation_tasks')
    op.drop_column('evaluation_tasks', 'task_category')

    task_category_enum = sa.Enum(
        'STANDARD', 'ATTACK',
        name='task_category_enum'
    )
    task_category_enum.drop(op.get_bind(), checkfirst=True)
