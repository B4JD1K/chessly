"""Add bot games

Revision ID: 004
Revises: 003
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'bot_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('player_color', sa.String(length=10), server_default='white', nullable=False),
        sa.Column('difficulty', sa.String(length=20), server_default='medium', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('result', sa.String(length=20), nullable=True),
        sa.Column('current_fen', sa.String(length=100), server_default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', nullable=False),
        sa.Column('moves', sa.Text(), server_default='', nullable=False),
        sa.Column('pgn', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bot_games_player_id'), 'bot_games', ['player_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_bot_games_player_id'), table_name='bot_games')
    op.drop_table('bot_games')
