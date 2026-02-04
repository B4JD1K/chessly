from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.puzzle import Puzzle


class PuzzleVariant(Base):
    __tablename__ = "puzzle_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    puzzle_id: Mapped[int] = mapped_column(ForeignKey("puzzles.id", ondelete="CASCADE"))
    move_sequence: Mapped[str] = mapped_column(Text)  # UCI moves to reach this position
    response_move: Mapped[str] = mapped_column(String(10))  # Correct response in UCI
    is_mainline: Mapped[bool] = mapped_column(default=False)

    puzzle: Mapped["Puzzle"] = relationship("Puzzle", back_populates="variants")

    @property
    def moves_list(self) -> list[str]:
        return self.move_sequence.split() if self.move_sequence else []
