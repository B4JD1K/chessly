"""Initial tables

Revision ID: 001
Revises:
Create Date: 2024-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False, server_default='1200'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'puzzles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fen', sa.String(length=100), nullable=False),
        sa.Column('solution', sa.Text(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False, server_default='1500'),
        sa.Column('themes', sa.Text(), nullable=True),
        sa.Column('daily_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_puzzles_daily_date'), 'puzzles', ['daily_date'], unique=True)

    op.create_table(
        'puzzle_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('puzzle_id', sa.Integer(), nullable=False),
        sa.Column('move_sequence', sa.Text(), nullable=False),
        sa.Column('response_move', sa.String(length=10), nullable=False),
        sa.Column('is_mainline', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['puzzle_id'], ['puzzles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('puzzle_variants')
    op.drop_index(op.f('ix_puzzles_daily_date'), table_name='puzzles')
    op.drop_table('puzzles')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
