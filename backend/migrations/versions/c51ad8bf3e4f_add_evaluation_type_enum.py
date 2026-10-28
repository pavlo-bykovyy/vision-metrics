"""add_evaluation_type_enum

Revision ID: c51ad8bf3e4f
Revises: 6544461b84c7
Create Date: 2026-08-24 13:14:39.396656

"""
from alembic import op
import sqlalchemy as sa


revision = 'c51ad8bf3e4f'
down_revision = '6544461b84c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    evaluation_type_enum = sa.Enum(
        'NONE', 'BASE_MODEL', 'LORA',
        name='evaluation_type_enum'
    )

    evaluation_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('evaluation_tasks', sa.Column('evaluation_type', evaluation_type_enum, nullable=True))


def downgrade() -> None:
    op.drop_column('evaluation_tasks', 'evaluation_type')

    evaluation_type_enum = sa.Enum(
        'NONE', 'BASE_MODEL', 'LORA',
        name='evaluation_type_enum'
    )

    evaluation_type_enum.drop(op.get_bind(), checkfirst=True)