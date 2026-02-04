from datetime import datetime
from typing import Optional

import chess
from sqlalchemy.orm import Session

from app.models import (
    User,
    GameSession,
    GameMove,
    GameStatus,
    GameResult,
    TimeControl,
    TIME_CONTROL_SETTINGS,
)
from app.schemas import GameCreate, GameMoveRequest, GameMoveResponse


class GameService:
    def __init__(self, db: Session):
        self.db = db

    def create_game(self, creator: User, game_data: GameCreate) -> GameSession:
        """Create a new game and assign the creator as white player."""
        time_settings = TIME_CONTROL_SETTINGS[game_data.time_control]

        game = GameSession(
            white_player_id=creator.id,
            time_control=game_data.time_control.value,
            white_time_remaining=time_settings["initial"],
            black_time_remaining=time_settings["initial"],
            status=GameStatus.WAITING.value,
        )

        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def get_game_by_code(self, code: str) -> Optional[GameSession]:
        """Get a game by its unique code."""
        return (
            self.db.query(GameSession)
            .filter(GameSession.code == code)
            .first()
        )

    def get_game_by_id(self, game_id: int) -> Optional[GameSession]:
        """Get a game by its ID."""
        return (
            self.db.query(GameSession)
            .filter(GameSession.id == game_id)
            .first()
        )

    def join_game(self, game: GameSession, player: User) -> tuple[bool, str]:
        """
        Join an existing game as the black player.

        Returns (success, message/color).
        """
        if game.status != GameStatus.WAITING.value:
            return False, "Game is not accepting players"

        if game.white_player_id == player.id:
            return True, "white"  # Already in the game as white

        if game.black_player_id is not None:
            if game.black_player_id == player.id:
                return True, "black"  # Already in the game as black
            return False, "Game is full"

        # Join as black
        game.black_player_id = player.id
        game.status = GameStatus.ACTIVE.value
        game.started_at = datetime.utcnow()

        self.db.commit()
        return True, "black"

    def make_move(
        self,
        game: GameSession,
        player: User,
        move_request: GameMoveRequest,
    ) -> GameMoveResponse:
        """
        Process a move in the game.

        Validates the move, updates game state, and checks for game over.
        """
        if game.status != GameStatus.ACTIVE.value:
            return GameMoveResponse(
                valid=False,
                message="Game is not active"
            )

        # Check if it's the player's turn
        is_white = game.white_player_id == player.id
        is_black = game.black_player_id == player.id

        if not (is_white or is_black):
            return GameMoveResponse(
                valid=False,
                message="You are not a player in this game"
            )

        if game.is_white_turn and not is_white:
            return GameMoveResponse(
                valid=False,
                message="It's not your turn"
            )

        if not game.is_white_turn and not is_black:
            return GameMoveResponse(
                valid=False,
                message="It's not your turn"
            )

        # Validate move with python-chess
        board = chess.Board(game.current_fen)

        try:
            move = chess.Move.from_uci(move_request.move)
        except ValueError:
            return GameMoveResponse(
                valid=False,
                message="Invalid move format"
            )

        if move not in board.legal_moves:
            return GameMoveResponse(
                valid=False,
                message="Illegal move"
            )

        # Get SAN notation before making the move
        move_san = board.san(move)

        # Make the move
        board.push(move)
        new_fen = board.fen()

        # Update time
        time_settings = TIME_CONTROL_SETTINGS[TimeControl(game.time_control)]
        if is_white:
            game.white_time_remaining -= move_request.time_spent // 1000
            game.white_time_remaining += time_settings["increment"]
            game.white_time_remaining = max(0, game.white_time_remaining)
        else:
            game.black_time_remaining -= move_request.time_spent // 1000
            game.black_time_remaining += time_settings["increment"]
            game.black_time_remaining = max(0, game.black_time_remaining)

        # Record the move
        move_number = len(game.moves) + 1
        game_move = GameMove(
            game_id=game.id,
            move_number=move_number,
            move_uci=move_request.move,
            move_san=move_san,
            fen_after=new_fen,
            time_spent=move_request.time_spent,
        )
        self.db.add(game_move)

        # Update game state
        game.current_fen = new_fen
        game.last_move_at = datetime.utcnow()

        # Check for game over
        game_over = False
        result = None

        if board.is_checkmate():
            game_over = True
            result = GameResult.WHITE_WIN if not game.is_white_turn else GameResult.BLACK_WIN
            game.status = GameStatus.COMPLETED.value
            game.result = result.value
            game.ended_at = datetime.utcnow()

        elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            game_over = True
            result = GameResult.DRAW
            game.status = GameStatus.COMPLETED.value
            game.result = result.value
            game.ended_at = datetime.utcnow()

        self.db.commit()

        return GameMoveResponse(
            valid=True,
            move_san=move_san,
            fen_after=new_fen,
            game_over=game_over,
            result=result,
        )

    def timeout_game(self, game: GameSession, timed_out_color: str) -> GameResult:
        """Handle game timeout."""
        if timed_out_color == "white":
            result = GameResult.BLACK_WIN
        else:
            result = GameResult.WHITE_WIN

        game.status = GameStatus.COMPLETED.value
        game.result = result.value
        game.ended_at = datetime.utcnow()

        self.db.commit()
        return result

    def resign_game(self, game: GameSession, player: User) -> GameResult:
        """Handle player resignation."""
        is_white = game.white_player_id == player.id

        if is_white:
            result = GameResult.BLACK_WIN
        else:
            result = GameResult.WHITE_WIN

        game.status = GameStatus.COMPLETED.value
        game.result = result.value
        game.ended_at = datetime.utcnow()

        self.db.commit()
        return result

    def get_player_color(self, game: GameSession, player: User) -> Optional[str]:
        """Get the color a player is playing as in a game."""
        if game.white_player_id == player.id:
            return "white"
        elif game.black_player_id == player.id:
            return "black"
        return None
