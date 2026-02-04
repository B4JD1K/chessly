import aiohttp
from dataclasses import dataclass
from typing import Optional

from config import config


@dataclass
class PuzzleData:
    id: int
    fen: str
    rating: int
    themes: list[str]
    player_color: str


@dataclass
class StreakData:
    current_streak: int
    best_streak: int
    puzzle_solved_today: bool


@dataclass
class LessonData:
    id: int
    title: str
    description: Optional[str]
    category: str
    level: str
    steps_count: int


@dataclass
class LessonProgressData:
    lesson_id: int
    status: str
    current_step_index: int
    total_steps: int


@dataclass
class CategoryProgressData:
    category: str
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int


@dataclass
class UserStatsData:
    puzzles_solved: int
    lessons_completed: int
    games_won: int
    current_streak: int
    best_streak: int


class APIClient:
    def __init__(self):
        self.base_url = config.API_BASE_URL

    async def get_daily_puzzle(self) -> Optional[PuzzleData]:
        """Fetch the daily puzzle from the backend."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/puzzles/daily") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return PuzzleData(
                            id=data["id"],
                            fen=data["fen"],
                            rating=data["rating"],
                            themes=data["themes"],
                            player_color=data["player_color"],
                        )
                    return None
            except Exception as e:
                print(f"API error: {e}")
                return None

    async def get_user_streak(self, discord_id: str) -> Optional[StreakData]:
        """Get user's streak information."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/users/{discord_id}/streak") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return StreakData(
                            current_streak=data["current_streak"],
                            best_streak=data["best_streak"],
                            puzzle_solved_today=data["puzzle_solved_today"],
                        )
                    return None
            except Exception as e:
                print(f"API error: {e}")
                return None

    async def sync_user(self, discord_id: str, username: str, avatar_url: Optional[str] = None):
        """Sync user with backend."""
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "discord_id": discord_id,
                    "username": username,
                    "avatar_url": avatar_url,
                }
                async with session.post(f"{self.base_url}/users/sync", json=payload) as resp:
                    return resp.status == 200
            except Exception as e:
                print(f"API error: {e}")
                return False

    async def get_recommended_lesson(self, discord_id: str) -> Optional[LessonData]:
        """Get recommended lesson for user."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/lessons/recommended?discord_id={discord_id}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return LessonData(
                                id=data["id"],
                                title=data["title"],
                                description=data.get("description"),
                                category=data["category"],
                                level=data["level"],
                                steps_count=data["steps_count"],
                            )
                    return None
            except Exception as e:
                print(f"API error: {e}")
                return None

    async def get_category_progress(self, discord_id: str) -> list[CategoryProgressData]:
        """Get user's progress in each category."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/lessons/category-progress?discord_id={discord_id}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [
                            CategoryProgressData(
                                category=item["category"],
                                total_lessons=item["total_lessons"],
                                completed_lessons=item["completed_lessons"],
                                in_progress_lessons=item["in_progress_lessons"],
                            )
                            for item in data
                        ]
                    return []
            except Exception as e:
                print(f"API error: {e}")
                return []

    async def get_user_stats(self, discord_id: str) -> Optional[UserStatsData]:
        """Get user's stats for achievements."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/achievements/user/{discord_id}/stats"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return UserStatsData(
                            puzzles_solved=data.get("puzzles_solved", 0),
                            lessons_completed=data.get("lessons_completed", 0),
                            games_won=data.get("games_won", 0),
                            current_streak=data.get("current_streak", 0),
                            best_streak=data.get("best_streak", 0),
                        )
                    return None
            except Exception as e:
                print(f"API error: {e}")
                return None


api_client = APIClient()
