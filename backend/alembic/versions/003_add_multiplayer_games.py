"""Add multiplayer games

Revision ID: 003
Revises: 002
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create game_sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=8), nullable=False),
        sa.Column('white_player_id', sa.Integer(), nullable=True),
        sa.Column('black_player_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='waiting', nullable=False),
        sa.Column('result', sa.String(length=20), nullable=True),
        sa.Column('current_fen', sa.String(length=100), server_default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', nullable=False),
        sa.Column('time_control', sa.String(length=20), server_default='blitz_5', nullable=False),
        sa.Column('white_time_remaining', sa.Integer(), server_default='300', nullable=False),
        sa.Column('black_time_remaining', sa.Integer(), server_default='300', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_move_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['white_player_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['black_player_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_sessions_code'), 'game_sessions', ['code'], unique=True)

    # Create game_moves table
    op.create_table(
        'game_moves',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('move_number', sa.Integer(), nullable=False),
        sa.Column('move_uci', sa.String(length=10), nullable=False),
        sa.Column('move_san', sa.String(length=10), nullable=False),
        sa.Column('fen_after', sa.String(length=100), nullable=False),
        sa.Column('time_spent', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_moves_game_id'), 'game_moves', ['game_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_game_moves_game_id'), table_name='game_moves')
    op.drop_table('game_moves')
    op.drop_index(op.f('ix_game_sessions_code'), table_name='game_sessions')
    op.drop_table('game_sessions')
