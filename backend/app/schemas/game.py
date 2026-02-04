from datetime import datetime
from pydantic import BaseModel

from app.models.game import TimeControl, GameStatus, GameResult


class GameCreate(BaseModel):
    time_control: TimeControl = TimeControl.BLITZ_5


class GameJoin(BaseModel):
    code: str


class PlayerInfo(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class GameMoveSchema(BaseModel):
    move_number: int
    move_uci: str
    move_san: str
    fen_after: str
    time_spent: int

    model_config = {"from_attributes": True}


class GameResponse(BaseModel):
    id: int
    code: str
    status: GameStatus
    result: GameResult | None = None
    current_fen: str
    time_control: TimeControl
    white_time_remaining: int
    black_time_remaining: int
    white_player: PlayerInfo | None = None
    black_player: PlayerInfo | None = None
    is_white_turn: bool
    move_count: int
    created_at: datetime
    started_at: datetime | None = None

    model_config = {"from_attributes": True}


class GameMoveRequest(BaseModel):
    move: str  # UCI format (e.g., "e2e4")
    time_spent: int = 0  # milliseconds spent on this move


class GameMoveResponse(BaseModel):
    valid: bool
    move_san: str | None = None
    fen_after: str | None = None
    game_over: bool = False
    result: GameResult | None = None
    message: str | None = None


# WebSocket message types
class WSMessage(BaseModel):
    type: str
    data: dict


class WSMoveMessage(BaseModel):
    type: str = "move"
    move_uci: str
    move_san: str
    fen: str
    white_time: int
    black_time: int
    is_white_turn: bool


class WSGameOverMessage(BaseModel):
    type: str = "game_over"
    result: GameResult
    reason: str


class WSPlayerJoinedMessage(BaseModel):
    type: str = "player_joined"
    player: PlayerInfo
    color: str  # "white" or "black"


class WSGameStartMessage(BaseModel):
    type: str = "game_start"
    white_player: PlayerInfo
    black_player: PlayerInfo
    fen: str
    white_time: int
    black_time: int
