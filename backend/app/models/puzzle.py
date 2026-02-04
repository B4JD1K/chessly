from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.puzzle_variant import PuzzleVariant


class Puzzle(Base):
    __tablename__ = "puzzles"

    id: Mapped[int] = mapped_column(primary_key=True)
    fen: Mapped[str] = mapped_column(String(100))
    solution: Mapped[str] = mapped_column(Text)  # UCI moves separated by space
    rating: Mapped[int] = mapped_column(default=1500)
    themes: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    daily_date: Mapped[date | None] = mapped_column(Date, nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    variants: Mapped[list["PuzzleVariant"]] = relationship(
        "PuzzleVariant", back_populates="puzzle", cascade="all, delete-orphan"
    )

    @property
    def solution_moves(self) -> list[str]:
        return self.solution.split()
