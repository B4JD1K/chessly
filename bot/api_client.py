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


api_client = APIClient()
