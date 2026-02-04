from datetime import date
from pydantic import BaseModel


class UserCreate(BaseModel):
    discord_id: str
    username: str
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: int
    discord_id: str
    username: str
    avatar_url: str | None
    rating: int
    current_streak: int
    best_streak: int
    last_puzzle_date: date | None

    model_config = {"from_attributes": True}


class StreakResponse(BaseModel):
    current_streak: int
    best_streak: int
    last_puzzle_date: date | None
    puzzle_solved_today: bool
