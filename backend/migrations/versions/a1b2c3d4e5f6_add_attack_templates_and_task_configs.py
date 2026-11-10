"""add_attack_templates_and_task_configs

Revision ID: a1b2c3d4e5f6
Revises: dcce5e1e4e9f
Create Date: 2026-10-19 17:45:00.000000

"""
import json
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'dcce5e1e4e9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'attack_task_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=80), nullable=False),
        sa.Column('expected_output_format', sa.String(length=50), nullable=False, server_default='free_text'),
        sa.Column('max_new_tokens', sa.Integer(), nullable=False, server_default='180'),
        sa.Column('languages_config', sa.JSON(), nullable=False),
        sa.Column('default_entities', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attack_task_configs_id'), 'attack_task_configs', ['id'], unique=False)
    op.create_index(op.f('ix_attack_task_configs_task_name'), 'attack_task_configs', ['task_name'], unique=True)

    op.create_table(
        'attack_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=80), nullable=False, server_default='heroes'),
        sa.Column('key', sa.String(length=80), nullable=False),
        sa.Column('metric_category', sa.String(length=80), nullable=False),
        sa.Column('variant', sa.String(length=40), nullable=True),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('check_canary', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('text', sa.JSON(), nullable=False),
        sa.Column('ground_truth', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attack_templates_id'), 'attack_templates', ['id'], unique=False)
    op.create_index(op.f('ix_attack_templates_task_name'), 'attack_templates', ['task_name'], unique=False)
    op.create_index(op.f('ix_attack_templates_key'), 'attack_templates', ['key'], unique=False)
    op.create_index(op.f('ix_attack_templates_metric_category'), 'attack_templates', ['metric_category'], unique=False)

    op.create_table(
        'attack_techniques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=80), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('templates', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attack_techniques_id'), 'attack_techniques', ['id'], unique=False)
    op.create_index(op.f('ix_attack_techniques_key'), 'attack_techniques', ['key'], unique=True)

    # Initial seed from INITIAL_TASK_CONFIGS, INITIAL_ATTACK_TEMPLATES, and INITIAL_ATTACK_TECHNIQUES
    from api_llm.attacks.seed_defaults import (
        INITIAL_TASK_CONFIGS,
        INITIAL_ATTACK_TEMPLATES,
        INITIAL_ATTACK_TECHNIQUES,
    )

    task_configs_table = sa.table(
        'attack_task_configs',
        sa.column('task_name', sa.String),
        sa.column('expected_output_format', sa.String),
        sa.column('max_new_tokens', sa.Integer),
        sa.column('languages_config', sa.JSON),
        sa.column('default_entities', sa.JSON),
    )
    op.bulk_insert(task_configs_table, INITIAL_TASK_CONFIGS)

    templates_table = sa.table(
        'attack_templates',
        sa.column('task_name', sa.String),
        sa.column('key', sa.String),
        sa.column('metric_category', sa.String),
        sa.column('variant', sa.String),
        sa.column('goal', sa.Text),
        sa.column('check_canary', sa.Boolean),
        sa.column('is_enabled', sa.Boolean),
        sa.column('text', sa.JSON),
        sa.column('ground_truth', sa.JSON),
    )
    op.bulk_insert(templates_table, INITIAL_ATTACK_TEMPLATES)

    techniques_table = sa.table(
        'attack_techniques',
        sa.column('key', sa.String),
        sa.column('is_enabled', sa.Boolean),
        sa.column('templates', sa.JSON),
    )
    op.bulk_insert(techniques_table, INITIAL_ATTACK_TECHNIQUES)


def downgrade() -> None:
    op.drop_index(op.f('ix_attack_techniques_key'), table_name='attack_techniques')
    op.drop_index(op.f('ix_attack_techniques_id'), table_name='attack_techniques')
    op.drop_table('attack_techniques')

    op.drop_index(op.f('ix_attack_templates_metric_category'), table_name='attack_templates')
    op.drop_index(op.f('ix_attack_templates_key'), table_name='attack_templates')
    op.drop_index(op.f('ix_attack_templates_task_name'), table_name='attack_templates')
    op.drop_index(op.f('ix_attack_templates_id'), table_name='attack_templates')
    op.drop_table('attack_templates')

    op.drop_index(op.f('ix_attack_task_configs_task_name'), table_name='attack_task_configs')
    op.drop_index(op.f('ix_attack_task_configs_id'), table_name='attack_task_configs')
    op.drop_table('attack_task_configs')

