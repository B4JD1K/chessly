from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
import secrets

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class GameStatus(str, Enum):
    WAITING = "waiting"  # Waiting for opponent
    ACTIVE = "active"  # Game in progress
    COMPLETED = "completed"  # Game finished
    ABANDONED = "abandoned"  # Player left


class GameResult(str, Enum):
    WHITE_WIN = "white_win"
    BLACK_WIN = "black_win"
    DRAW = "draw"
    ABANDONED = "abandoned"


class TimeControl(str, Enum):
    BULLET_1 = "bullet_1"  # 1+0
    BULLET_2 = "bullet_2"  # 2+1
    BLITZ_3 = "blitz_3"  # 3+0
    BLITZ_5 = "blitz_5"  # 5+0
    RAPID_10 = "rapid_10"  # 10+0
    RAPID_15 = "rapid_15"  # 15+10


TIME_CONTROL_SETTINGS = {
    TimeControl.BULLET_1: {"initial": 60, "increment": 0},
    TimeControl.BULLET_2: {"initial": 120, "increment": 1},
    TimeControl.BLITZ_3: {"initial": 180, "increment": 0},
    TimeControl.BLITZ_5: {"initial": 300, "increment": 0},
    TimeControl.RAPID_10: {"initial": 600, "increment": 0},
    TimeControl.RAPID_15: {"initial": 900, "increment": 10},
}


def generate_game_code() -> str:
    """Generate a unique 8-character game code."""
    return secrets.token_urlsafe(6)[:8]


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(
        String(8), unique=True, index=True, default=generate_game_code
    )

    # Players (nullable for anonymous games)
    white_player_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    black_player_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Guest names for anonymous players
    white_guest_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    black_guest_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Creator's chosen color ("white" or "black" or "random" -> resolved)
    creator_color: Mapped[str] = mapped_column(String(10), default="white")

    # Game state
    status: Mapped[str] = mapped_column(
        String(20), default=GameStatus.WAITING.value
    )
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    current_fen: Mapped[str] = mapped_column(
        String(100),
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )

    # Time control
    time_control: Mapped[str] = mapped_column(
        String(20), default=TimeControl.BLITZ_5.value
    )
    white_time_remaining: Mapped[int] = mapped_column(Integer, default=300)  # seconds
    black_time_remaining: Mapped[int] = mapped_column(Integer, default=300)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_move_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    white_player: Mapped["User | None"] = relationship(
        "User", foreign_keys=[white_player_id]
    )
    black_player: Mapped["User | None"] = relationship(
        "User", foreign_keys=[black_player_id]
    )
    moves: Mapped[list["GameMove"]] = relationship(
        "GameMove", back_populates="game", cascade="all, delete-orphan"
    )

    @property
    def is_white_turn(self) -> bool:
        """Check if it's white's turn based on FEN."""
        return " w " in self.current_fen

    @property
    def move_count(self) -> int:
        """Get the number of moves played."""
        return len(self.moves)


class GameMove(Base):
    __tablename__ = "game_moves"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game_sessions.id", ondelete="CASCADE")
    )
    move_number: Mapped[int] = mapped_column(Integer)
    move_uci: Mapped[str] = mapped_column(String(10))  # e.g., "e2e4"
    move_san: Mapped[str] = mapped_column(String(10))  # e.g., "e4"
    fen_after: Mapped[str] = mapped_column(String(100))
    time_spent: Mapped[int] = mapped_column(Integer, default=0)  # milliseconds
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    game: Mapped["GameSession"] = relationship("GameSession", back_populates="moves")
