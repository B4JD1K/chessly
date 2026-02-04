from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AchievementResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str
    icon: Optional[str] = None
    threshold: int

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    achievement: AchievementResponse
    unlocked_at: datetime

    class Config:
        from_attributes = True


class AchievementUnlockedResponse(BaseModel):
    """Returned when an achievement is newly unlocked"""
    achievement: AchievementResponse
    is_new: bool = True


class UserAchievementsListResponse(BaseModel):
    unlocked: list[UserAchievementResponse]
    locked: list[AchievementResponse]
    total_unlocked: int
    total_available: int
