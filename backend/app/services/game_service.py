from datetime import datetime
from typing import Optional
import random

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

    def create_game(
        self,
        creator: Optional[User],
        game_data: GameCreate,
        guest_name: Optional[str] = None,
    ) -> GameSession:
        """
        Create a new game.

        Args:
            creator: User object if logged in, None for anonymous
            game_data: Game creation parameters
            guest_name: Guest name for anonymous players
        """
        time_settings = TIME_CONTROL_SETTINGS[game_data.time_control]

        # Resolve random color
        color = game_data.color
        if color == "random":
            color = random.choice(["white", "black"])

        # Determine player assignment based on color choice
        if color == "white":
            white_player_id = creator.id if creator else None
            white_guest_name = guest_name if not creator else None
            black_player_id = None
            black_guest_name = None
        else:
            white_player_id = None
            white_guest_name = None
            black_player_id = creator.id if creator else None
            black_guest_name = guest_name if not creator else None

        game = GameSession(
            white_player_id=white_player_id,
            black_player_id=black_player_id,
            white_guest_name=white_guest_name,
            black_guest_name=black_guest_name,
            creator_color=color,
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

    def join_game(
        self,
        game: GameSession,
        player: Optional[User] = None,
        guest_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Join an existing game as the opponent.

        Args:
            game: The game to join
            player: User object if logged in, None for anonymous
            guest_name: Guest name for anonymous players

        Returns (success, message/color).
        """
        if game.status != GameStatus.WAITING.value:
            return False, "Game is not accepting players"

        # Check if player is already in the game
        if player:
            if game.white_player_id == player.id:
                return True, "white"
            if game.black_player_id == player.id:
                return True, "black"

        # Determine which slot to fill (opposite of creator)
        if game.creator_color == "white":
            # Creator is white, joiner takes black
            if game.black_player_id is not None or game.black_guest_name is not None:
                return False, "Game is full"

            if player:
                game.black_player_id = player.id
            else:
                game.black_guest_name = guest_name or "Guest"

            game.status = GameStatus.ACTIVE.value
            game.started_at = datetime.utcnow()
            self.db.commit()
            return True, "black"
        else:
            # Creator is black, joiner takes white
            if game.white_player_id is not None or game.white_guest_name is not None:
                return False, "Game is full"

            if player:
                game.white_player_id = player.id
            else:
                game.white_guest_name = guest_name or "Guest"

            game.status = GameStatus.ACTIVE.value
            game.started_at = datetime.utcnow()
            self.db.commit()
            return True, "white"

    def make_move(
        self,
        game: GameSession,
        player: Optional[User],
        move_request: GameMoveRequest,
        guest_session_id: Optional[str] = None,
        is_white_player: Optional[bool] = None,
    ) -> GameMoveResponse:
        """
        Process a move in the game.

        Args:
            game: The game session
            player: User object if logged in, None for anonymous
            move_request: The move to make
            guest_session_id: Session ID for anonymous players (unused but kept for future)
            is_white_player: For anonymous players, explicitly specify color

        Validates the move, updates game state, and checks for game over.
        """
        if game.status != GameStatus.ACTIVE.value:
            return GameMoveResponse(
                valid=False,
                message="Game is not active"
            )

        # Check if it's the player's turn
        if player:
            is_white = game.white_player_id == player.id
            is_black = game.black_player_id == player.id
        else:
            # Anonymous player - use explicit color
            is_white = is_white_player is True
            is_black = is_white_player is False

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

    def resign_game(
        self,
        game: GameSession,
        player: Optional[User] = None,
        is_white_resigning: Optional[bool] = None,
    ) -> GameResult:
        """Handle player resignation."""
        if player:
            is_white = game.white_player_id == player.id
        else:
            is_white = is_white_resigning is True

        if is_white:
            result = GameResult.BLACK_WIN
        else:
            result = GameResult.WHITE_WIN

        game.status = GameStatus.COMPLETED.value
        game.result = result.value
        game.ended_at = datetime.utcnow()

        self.db.commit()
        return result

    def get_player_color(
        self,
        game: GameSession,
        player: Optional[User] = None,
    ) -> Optional[str]:
        """Get the color a player is playing as in a game."""
        if player:
            if game.white_player_id == player.id:
                return "white"
            elif game.black_player_id == player.id:
                return "black"
        return None

    def has_anonymous_player(self, game: GameSession, color: str) -> bool:
        """Check if a color slot is occupied by an anonymous player."""
        if color == "white":
            return game.white_guest_name is not None and game.white_player_id is None
        else:
            return game.black_guest_name is not None and game.black_player_id is None
