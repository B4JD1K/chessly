from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    BotGameCreate,
    BotGameResponse,
    BotMoveRequest,
    BotMoveResponse,
)
from app.services.user_service import UserService
from app.services.bot_game_service import BotGameService
from app.services.stockfish_service import BotDifficulty, DIFFICULTY_SETTINGS

router = APIRouter()


@router.get("/difficulties")
def get_difficulties():
    """Get available difficulty levels with their ELO ratings."""
    return {
        diff.value: {
            "name": diff.value.title(),
            "elo": settings["elo"],
        }
        for diff, settings in DIFFICULTY_SETTINGS.items()
    }


@router.post("", response_model=BotGameResponse)
def create_bot_game(
    game_data: BotGameCreate,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Create a new game against the bot."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bot_service = BotGameService(db)

    try:
        game = bot_service.create_game(user, game_data)
        return BotGameResponse.from_bot_game(game)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Stockfish engine not available: {e}"
        )


@router.get("/{game_id}", response_model=BotGameResponse)
def get_bot_game(
    game_id: int,
    db: Session = Depends(get_db),
):
    """Get bot game details."""
    bot_service = BotGameService(db)
    game = bot_service.get_game_by_id(game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return BotGameResponse.from_bot_game(game)


@router.post("/{game_id}/move", response_model=BotMoveResponse)
def make_move(
    game_id: int,
    move_request: BotMoveRequest,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Make a move in the bot game."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bot_service = BotGameService(db)
    game = bot_service.get_game_by_id(game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    try:
        return bot_service.make_move(game, user, move_request)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Stockfish engine error: {e}"
        )


@router.post("/{game_id}/resign")
def resign_game(
    game_id: int,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Resign from the bot game."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bot_service = BotGameService(db)
    game = bot_service.get_game_by_id(game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != "active":
        raise HTTPException(status_code=400, detail="Game is not active")

    try:
        result = bot_service.resign(game, user)
        return {"result": result.value}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{game_id}/pgn", response_class=PlainTextResponse)
def get_pgn(
    game_id: int,
    db: Session = Depends(get_db),
):
    """Get PGN for the game."""
    bot_service = BotGameService(db)
    game = bot_service.get_game_by_id(game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return bot_service.get_pgn(game)


@router.get("/user/{discord_id}/history", response_model=list[BotGameResponse])
def get_user_history(
    discord_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get user's bot game history."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bot_service = BotGameService(db)
    games = bot_service.get_user_games(user, limit)

    return [BotGameResponse.from_bot_game(g) for g in games]
