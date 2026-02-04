from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GameStatus
from app.schemas import (
    GameCreate,
    GameResponse,
    GameMoveRequest,
    GameMoveResponse,
    PlayerInfo,
)
from app.services import GameService, UserService, connection_manager

router = APIRouter()


def get_player_info(user) -> PlayerInfo | None:
    if user is None:
        return None
    return PlayerInfo(
        id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
    )


@router.post("", response_model=GameResponse)
def create_game(
    game_data: GameCreate,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """
    Create a new multiplayer game.

    Returns the game with a unique code that can be shared.
    """
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    game_service = GameService(db)
    game = game_service.create_game(user, game_data)

    return GameResponse(
        id=game.id,
        code=game.code,
        status=GameStatus(game.status),
        current_fen=game.current_fen,
        time_control=game.time_control,
        white_time_remaining=game.white_time_remaining,
        black_time_remaining=game.black_time_remaining,
        white_player=get_player_info(game.white_player),
        black_player=get_player_info(game.black_player),
        is_white_turn=game.is_white_turn,
        move_count=game.move_count,
        created_at=game.created_at,
        started_at=game.started_at,
    )


@router.get("/{code}", response_model=GameResponse)
def get_game(
    code: str,
    db: Session = Depends(get_db),
):
    """Get game details by code."""
    game_service = GameService(db)
    game = game_service.get_game_by_code(code)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameResponse(
        id=game.id,
        code=game.code,
        status=GameStatus(game.status),
        result=game.result,
        current_fen=game.current_fen,
        time_control=game.time_control,
        white_time_remaining=game.white_time_remaining,
        black_time_remaining=game.black_time_remaining,
        white_player=get_player_info(game.white_player),
        black_player=get_player_info(game.black_player),
        is_white_turn=game.is_white_turn,
        move_count=game.move_count,
        created_at=game.created_at,
        started_at=game.started_at,
    )


@router.post("/{code}/join", response_model=GameResponse)
def join_game(
    code: str,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Join an existing game as the black player."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    game_service = GameService(db)
    game = game_service.get_game_by_code(code)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    success, message = game_service.join_game(game, user)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Refresh to get updated relationships
    db.refresh(game)

    return GameResponse(
        id=game.id,
        code=game.code,
        status=GameStatus(game.status),
        current_fen=game.current_fen,
        time_control=game.time_control,
        white_time_remaining=game.white_time_remaining,
        black_time_remaining=game.black_time_remaining,
        white_player=get_player_info(game.white_player),
        black_player=get_player_info(game.black_player),
        is_white_turn=game.is_white_turn,
        move_count=game.move_count,
        created_at=game.created_at,
        started_at=game.started_at,
    )


@router.post("/{code}/move", response_model=GameMoveResponse)
def make_move(
    code: str,
    move_request: GameMoveRequest,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Make a move in the game."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    game_service = GameService(db)
    game = game_service.get_game_by_code(code)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return game_service.make_move(game, user, move_request)


@router.post("/{code}/resign")
def resign_game(
    code: str,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Resign from the game."""
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    game_service = GameService(db)
    game = game_service.get_game_by_code(code)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != GameStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Game is not active")

    color = game_service.get_player_color(game, user)
    if not color:
        raise HTTPException(status_code=400, detail="You are not in this game")

    result = game_service.resign_game(game, user)
    return {"result": result.value}


@router.websocket("/{code}/ws")
async def game_websocket(
    websocket: WebSocket,
    code: str,
    discord_id: str,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time game communication.

    Message types:
    - move: {type: "move", move: "e2e4", time_spent: 1000}
    - resign: {type: "resign"}
    - timeout: {type: "timeout", color: "white"|"black"}
    """
    user_service = UserService(db)
    user = user_service.get_user_by_discord_id(discord_id)

    if not user:
        await websocket.close(code=4004, reason="User not found")
        return

    game_service = GameService(db)
    game = game_service.get_game_by_code(code)

    if not game:
        await websocket.close(code=4004, reason="Game not found")
        return

    # Connect to the game room
    await connection_manager.connect(websocket, code, user.id)

    # Get player color
    color = game_service.get_player_color(game, user)

    # Notify others if a new player joined and game should start
    if game.status == GameStatus.ACTIVE.value and color:
        player_info = get_player_info(user)
        await connection_manager.broadcast_to_game(
            code,
            {
                "type": "player_joined",
                "player": player_info.model_dump(),
                "color": color,
            },
            exclude=websocket,
        )

        # If both players are connected, send game start
        if connection_manager.get_connection_count(code) == 2:
            await connection_manager.broadcast_to_all(
                code,
                {
                    "type": "game_start",
                    "white_player": get_player_info(game.white_player).model_dump(),
                    "black_player": get_player_info(game.black_player).model_dump(),
                    "fen": game.current_fen,
                    "white_time": game.white_time_remaining,
                    "black_time": game.black_time_remaining,
                },
            )

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "move":
                # Refresh game state
                db.refresh(game)

                move_request = GameMoveRequest(
                    move=data.get("move", ""),
                    time_spent=data.get("time_spent", 0),
                )

                result = game_service.make_move(game, user, move_request)

                if result.valid:
                    # Broadcast move to all players
                    db.refresh(game)
                    await connection_manager.broadcast_to_all(
                        code,
                        {
                            "type": "move",
                            "move_uci": data.get("move"),
                            "move_san": result.move_san,
                            "fen": result.fen_after,
                            "white_time": game.white_time_remaining,
                            "black_time": game.black_time_remaining,
                            "is_white_turn": game.is_white_turn,
                        },
                    )

                    if result.game_over:
                        await connection_manager.broadcast_to_all(
                            code,
                            {
                                "type": "game_over",
                                "result": result.result.value,
                                "reason": "checkmate" if "win" in result.result.value else "draw",
                            },
                        )
                else:
                    # Send error only to the player who made invalid move
                    await connection_manager.send_personal(
                        websocket,
                        {"type": "error", "message": result.message},
                    )

            elif msg_type == "resign":
                db.refresh(game)
                if game.status == GameStatus.ACTIVE.value:
                    result = game_service.resign_game(game, user)
                    await connection_manager.broadcast_to_all(
                        code,
                        {
                            "type": "game_over",
                            "result": result.value,
                            "reason": "resignation",
                        },
                    )

            elif msg_type == "timeout":
                db.refresh(game)
                timed_out_color = data.get("color")
                if game.status == GameStatus.ACTIVE.value and timed_out_color:
                    result = game_service.timeout_game(game, timed_out_color)
                    await connection_manager.broadcast_to_all(
                        code,
                        {
                            "type": "game_over",
                            "result": result.value,
                            "reason": "timeout",
                        },
                    )

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

        # Notify other player about disconnection
        await connection_manager.broadcast_to_game(
            code,
            {
                "type": "player_disconnected",
                "player_id": user.id,
                "color": color,
            },
        )
