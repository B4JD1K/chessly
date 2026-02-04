from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Date, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user_puzzle_progress import UserPuzzleProgress
    from app.models.user_lesson_progress import UserLessonProgress
    from app.models.achievement import UserAchievement


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[int] = mapped_column(default=1200)

    # Streak tracking
    current_streak: Mapped[int] = mapped_column(default=0)
    best_streak: Mapped[int] = mapped_column(default=0)
    last_puzzle_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Stats for achievements
    puzzles_solved: Mapped[int] = mapped_column(Integer, default=0)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    games_won: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    puzzle_progress: Mapped[list["UserPuzzleProgress"]] = relationship(
        "UserPuzzleProgress", back_populates="user", cascade="all, delete-orphan"
    )
    lesson_progress: Mapped[list["UserLessonProgress"]] = relationship(
        "UserLessonProgress", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
