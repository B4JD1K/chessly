from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # np. "FIRST_PUZZLE_SOLVED"
    name = Column(String(100), nullable=False)  # Nazwa wyświetlana
    description = Column(Text, nullable=False)  # Opis osiągnięcia
    icon = Column(String(50), nullable=True)  # Emoji lub ikona

    # Warunki odblokowania (JSON lub uproszczone)
    event_type = Column(String(50), nullable=False)  # Typ eventu: PUZZLE_SOLVED, STREAK_DAY, etc.
    threshold = Column(Integer, nullable=False, default=1)  # Ile razy event musi wystąpić

    # Czy achievement jest aktywny
    is_active = Column(Boolean, default=True)

    # Kolejność wyświetlania
    order_index = Column(Integer, default=0)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)

    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")
