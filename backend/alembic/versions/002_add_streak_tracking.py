"""Add streak tracking

Revision ID: 002
Revises: 001
Create Date: 2024-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update users table - add Discord fields and streak tracking
    op.add_column('users', sa.Column('discord_id', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('current_streak', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('best_streak', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('last_puzzle_date', sa.Date(), nullable=True))

    # Make discord_id unique and indexed (after populating existing rows if any)
    op.create_index(op.f('ix_users_discord_id'), 'users', ['discord_id'], unique=True)

    # Drop old columns that are no longer needed
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'email')
    op.drop_column('users', 'hashed_password')

    # Create user_puzzle_progress table
    op.create_table(
        'user_puzzle_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('puzzle_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='in_progress', nullable=False),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('current_move_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['puzzle_id'], ['puzzles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_puzzle_progress_user_puzzle'), 'user_puzzle_progress', ['user_id', 'puzzle_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_puzzle_progress_user_puzzle'), table_name='user_puzzle_progress')
    op.drop_table('user_puzzle_progress')

    op.add_column('users', sa.Column('hashed_password', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.drop_index(op.f('ix_users_discord_id'), table_name='users')
    op.drop_column('users', 'last_puzzle_date')
    op.drop_column('users', 'best_streak')
    op.drop_column('users', 'current_streak')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'discord_id')
