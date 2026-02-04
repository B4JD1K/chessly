from datetime import datetime
from typing import Optional

import chess
import chess.pgn
import io

from sqlalchemy.orm import Session

from app.models import User, BotGame, GameResult
from app.schemas import BotGameCreate, BotMoveRequest, BotMoveResponse
from app.services.stockfish_service import (
    get_stockfish_service,
    BotDifficulty,
    DIFFICULTY_SETTINGS,
)


class BotGameService:
    def __init__(self, db: Session):
        self.db = db
        self.stockfish = get_stockfish_service()

    def create_game(self, player: User, game_data: BotGameCreate) -> BotGame:
        """Create a new game against the bot."""
        game = BotGame(
            player_id=player.id,
            difficulty=game_data.difficulty.value,
            player_color=game_data.player_color,
            status="active",
        )

        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)

        # If player is black, bot makes the first move
        if game_data.player_color == "black":
            self._make_bot_move(game)
            self.db.commit()
            self.db.refresh(game)

        return game

    def get_game_by_id(self, game_id: int) -> Optional[BotGame]:
        """Get a bot game by ID."""
        return self.db.query(BotGame).filter(BotGame.id == game_id).first()

    def get_user_games(self, user: User, limit: int = 10) -> list[BotGame]:
        """Get recent bot games for a user."""
        return (
            self.db.query(BotGame)
            .filter(BotGame.player_id == user.id)
            .order_by(BotGame.created_at.desc())
            .limit(limit)
            .all()
        )

    def make_move(
        self,
        game: BotGame,
        player: User,
        move_request: BotMoveRequest,
    ) -> BotMoveResponse:
        """Process a player's move and get the bot's response."""
        if game.status != "active":
            return BotMoveResponse(
                valid=False,
                message="Game is not active"
            )

        if game.player_id != player.id:
            return BotMoveResponse(
                valid=False,
                message="You are not the player in this game"
            )

        if not game.is_player_turn:
            return BotMoveResponse(
                valid=False,
                message="It's not your turn"
            )

        # Validate the move
        board = chess.Board(game.current_fen)

        try:
            move = chess.Move.from_uci(move_request.move)
        except ValueError:
            return BotMoveResponse(
                valid=False,
                message="Invalid move format"
            )

        if move not in board.legal_moves:
            return BotMoveResponse(
                valid=False,
                message="Illegal move"
            )

        # Get SAN notation
        player_move_san = board.san(move)

        # Make the player's move
        board.push(move)
        game.add_move(move_request.move)
        game.current_fen = board.fen()

        # Check if game is over after player's move
        game_over, result = self._check_game_over(board)

        if game_over:
            game.status = "completed"
            game.result = result.value if result else None
            game.ended_at = datetime.utcnow()
            game.pgn = self._generate_pgn(game)
            self.db.commit()

            return BotMoveResponse(
                valid=True,
                player_move_san=player_move_san,
                fen_after=board.fen(),
                game_over=True,
                result=result,
            )

        # Bot's turn
        bot_move_uci = self._make_bot_move(game)
        board = chess.Board(game.current_fen)

        # Get bot move SAN (need to get it before push)
        bot_move = chess.Move.from_uci(bot_move_uci)
        board_before_bot = chess.Board(game.current_fen)
        # Go back one move to get the SAN
        moves_list = game.moves_list
        if len(moves_list) >= 2:
            temp_board = chess.Board()
            for m in moves_list[:-1]:
                temp_board.push(chess.Move.from_uci(m))
            bot_move_san = temp_board.san(bot_move)
        else:
            temp_board = chess.Board(game.current_fen)
            # This is a workaround - we need the board state before bot move
            bot_move_san = bot_move_uci

        # Check if game is over after bot's move
        game_over, result = self._check_game_over(chess.Board(game.current_fen))

        if game_over:
            game.status = "completed"
            game.result = result.value if result else None
            game.ended_at = datetime.utcnow()
            game.pgn = self._generate_pgn(game)

        self.db.commit()

        return BotMoveResponse(
            valid=True,
            player_move_san=player_move_san,
            bot_move_uci=bot_move_uci,
            bot_move_san=bot_move_san,
            fen_after=game.current_fen,
            game_over=game_over,
            result=result,
        )

    def resign(self, game: BotGame, player: User) -> GameResult:
        """Resign from the game."""
        if game.player_id != player.id:
            raise ValueError("Not your game")

        # Player resigns = bot wins
        if game.player_color == "white":
            result = GameResult.BLACK_WIN
        else:
            result = GameResult.WHITE_WIN

        game.status = "completed"
        game.result = result.value
        game.ended_at = datetime.utcnow()
        game.pgn = self._generate_pgn(game)

        self.db.commit()
        return result

    def _make_bot_move(self, game: BotGame) -> str:
        """Make a move for the bot."""
        difficulty = BotDifficulty(game.difficulty)
        bot_move = self.stockfish.get_best_move(game.current_fen, difficulty)

        board = chess.Board(game.current_fen)
        move = chess.Move.from_uci(bot_move)
        board.push(move)

        game.add_move(bot_move)
        game.current_fen = board.fen()

        return bot_move

    def _check_game_over(self, board: chess.Board) -> tuple[bool, Optional[GameResult]]:
        """Check if the game is over and return the result."""
        if board.is_checkmate():
            # The side to move is checkmated
            if board.turn == chess.WHITE:
                return True, GameResult.BLACK_WIN
            else:
                return True, GameResult.WHITE_WIN

        if board.is_stalemate():
            return True, GameResult.DRAW

        if board.is_insufficient_material():
            return True, GameResult.DRAW

        if board.can_claim_fifty_moves() or board.can_claim_threefold_repetition():
            return True, GameResult.DRAW

        return False, None

    def _generate_pgn(self, game: BotGame) -> str:
        """Generate PGN for the game."""
        pgn_game = chess.pgn.Game()

        # Set headers
        pgn_game.headers["Event"] = "Chessly Bot Game"
        pgn_game.headers["Site"] = "Chessly"
        pgn_game.headers["Date"] = game.created_at.strftime("%Y.%m.%d")

        difficulty = BotDifficulty(game.difficulty)
        bot_elo = DIFFICULTY_SETTINGS[difficulty]["elo"]

        if game.player_color == "white":
            pgn_game.headers["White"] = game.player.username
            pgn_game.headers["Black"] = f"Stockfish ({difficulty.value})"
            pgn_game.headers["WhiteElo"] = str(game.player.rating)
            pgn_game.headers["BlackElo"] = str(bot_elo)
        else:
            pgn_game.headers["White"] = f"Stockfish ({difficulty.value})"
            pgn_game.headers["Black"] = game.player.username
            pgn_game.headers["WhiteElo"] = str(bot_elo)
            pgn_game.headers["BlackElo"] = str(game.player.rating)

        if game.result:
            result_map = {
                GameResult.WHITE_WIN.value: "1-0",
                GameResult.BLACK_WIN.value: "0-1",
                GameResult.DRAW.value: "1/2-1/2",
            }
            pgn_game.headers["Result"] = result_map.get(game.result, "*")
        else:
            pgn_game.headers["Result"] = "*"

        # Add moves
        node = pgn_game
        board = chess.Board()

        for move_uci in game.moves_list:
            move = chess.Move.from_uci(move_uci)
            node = node.add_variation(move)
            board.push(move)

        # Convert to string
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        return pgn_game.accept(exporter)

    def get_pgn(self, game: BotGame) -> str:
        """Get PGN for the game, generating if needed."""
        if game.pgn:
            return game.pgn

        pgn = self._generate_pgn(game)
        game.pgn = pgn
        self.db.commit()
        return pgn
