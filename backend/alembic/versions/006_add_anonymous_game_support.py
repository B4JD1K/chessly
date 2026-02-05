"""Add anonymous game support

Revision ID: 006
Revises: 005
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add guest name columns for anonymous players
    op.add_column(
        "game_sessions",
        sa.Column("white_guest_name", sa.String(50), nullable=True),
    )
    op.add_column(
        "game_sessions",
        sa.Column("black_guest_name", sa.String(50), nullable=True),
    )
    # Add creator_color to track what color the game creator chose
    op.add_column(
        "game_sessions",
        sa.Column("creator_color", sa.String(10), nullable=True, server_default="white"),
    )


def downgrade() -> None:
    op.drop_column("game_sessions", "creator_color")
    op.drop_column("game_sessions", "black_guest_name")
    op.drop_column("game_sessions", "white_guest_name")
