"""add_judge_status

Revision ID: ffcb96f66f13
Revises: c669337d0a35
Create Date: 2026-08-23 17:55:40.683044

"""
from alembic import op
import sqlalchemy as sa


revision = 'ffcb96f66f13'
down_revision = 'c669337d0a35'
branch_labels = None
depends_on = None


def upgrade() -> None:
    judge_status_enum = sa.Enum(
        'NONE', 'PENDING', 'JUDGING', 'COMPLETED', 'CANCELLED', 'FAILED',
        name='judge_status_enum'
    )

    judge_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('evaluation_tasks', sa.Column('judge_status', judge_status_enum, nullable=True))


def downgrade() -> None:
    op.drop_column('evaluation_tasks', 'judge_status')

    judge_status_enum = sa.Enum(
        'NONE', 'PENDING', 'JUDGING', 'COMPLETED', 'CANCELLED', 'FAILED',
        name='judge_status_enum'
    )

    judge_status_enum.drop(op.get_bind(), checkfirst=True)