from datetime import datetime
from pydantic import BaseModel

from app.enums import BotDifficulty
from app.models.game import GameResult


class BotGameCreate(BaseModel):
    difficulty: BotDifficulty = BotDifficulty.MEDIUM
    player_color: str = "white"  # "white" or "black"


class BotGameResponse(BaseModel):
    id: int
    difficulty: BotDifficulty
    player_color: str
    status: str
    result: GameResult | None = None
    current_fen: str
    moves: list[str]
    move_count: int
    is_player_turn: bool
    created_at: datetime
    ended_at: datetime | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_bot_game(cls, game) -> "BotGameResponse":
        return cls(
            id=game.id,
            difficulty=BotDifficulty(game.difficulty),
            player_color=game.player_color,
            status=game.status,
            result=GameResult(game.result) if game.result else None,
            current_fen=game.current_fen,
            moves=game.moves_list,
            move_count=game.move_count,
            is_player_turn=game.is_player_turn,
            created_at=game.created_at,
            ended_at=game.ended_at,
        )


class BotMoveRequest(BaseModel):
    move: str  # UCI format


class BotMoveResponse(BaseModel):
    valid: bool
    player_move_san: str | None = None
    bot_move_uci: str | None = None
    bot_move_san: str | None = None
    fen_after: str | None = None
    game_over: bool = False
    result: GameResult | None = None
    message: str | None = None


class BotGamePGN(BaseModel):
    pgn: str
