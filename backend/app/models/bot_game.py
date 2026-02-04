from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.game import GameResult
from app.services.stockfish_service import BotDifficulty

if TYPE_CHECKING:
    from app.models.user import User


class BotGame(Base):
    __tablename__ = "bot_games"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Player
    player_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    player_color: Mapped[str] = mapped_column(String(10), default="white")

    # Bot settings
    difficulty: Mapped[str] = mapped_column(
        String(20), default=BotDifficulty.MEDIUM.value
    )

    # Game state
    status: Mapped[str] = mapped_column(String(20), default="active")
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    current_fen: Mapped[str] = mapped_column(
        String(100),
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )

    # Move history (space-separated UCI moves)
    moves: Mapped[str] = mapped_column(Text, default="")

    # PGN
    pgn: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    player: Mapped["User"] = relationship("User")

    @property
    def moves_list(self) -> list[str]:
        """Get moves as a list."""
        return self.moves.split() if self.moves else []

    @property
    def move_count(self) -> int:
        """Get the number of moves played."""
        return len(self.moves_list)

    @property
    def is_player_turn(self) -> bool:
        """Check if it's the player's turn."""
        fen_parts = self.current_fen.split()
        current_turn = fen_parts[1] if len(fen_parts) > 1 else "w"

        if self.player_color == "white":
            return current_turn == "w"
        else:
            return current_turn == "b"

    def add_move(self, move: str):
        """Add a move to the history."""
        if self.moves:
            self.moves = f"{self.moves} {move}"
        else:
            self.moves = move
