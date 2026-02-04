import asyncio
from enum import Enum
from typing import Optional
import chess
import chess.engine


class BotDifficulty(str, Enum):
    BEGINNER = "beginner"      # ~800 ELO
    EASY = "easy"              # ~1000 ELO
    MEDIUM = "medium"          # ~1400 ELO
    HARD = "hard"              # ~1800 ELO
    EXPERT = "expert"          # ~2200 ELO
    MASTER = "master"          # ~2500+ ELO


# Stockfish settings for each difficulty level
DIFFICULTY_SETTINGS = {
    BotDifficulty.BEGINNER: {
        "skill_level": 1,
        "elo": 800,
        "time_limit": 0.1,
        "depth": 5,
    },
    BotDifficulty.EASY: {
        "skill_level": 5,
        "elo": 1000,
        "time_limit": 0.2,
        "depth": 8,
    },
    BotDifficulty.MEDIUM: {
        "skill_level": 10,
        "elo": 1400,
        "time_limit": 0.3,
        "depth": 12,
    },
    BotDifficulty.HARD: {
        "skill_level": 15,
        "elo": 1800,
        "time_limit": 0.5,
        "depth": 15,
    },
    BotDifficulty.EXPERT: {
        "skill_level": 18,
        "elo": 2200,
        "time_limit": 1.0,
        "depth": 18,
    },
    BotDifficulty.MASTER: {
        "skill_level": 20,
        "elo": 2800,
        "time_limit": 2.0,
        "depth": 20,
    },
}


class StockfishService:
    """
    Service for interacting with Stockfish chess engine.

    Uses python-chess's engine interface for communication.
    """

    def __init__(self, stockfish_path: str = "stockfish"):
        self.stockfish_path = stockfish_path
        self._engine: Optional[chess.engine.SimpleEngine] = None

    def _get_engine(self) -> chess.engine.SimpleEngine:
        """Get or create engine instance."""
        if self._engine is None:
            try:
                self._engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            except Exception as e:
                raise RuntimeError(f"Failed to start Stockfish: {e}")
        return self._engine

    def close(self):
        """Close the engine."""
        if self._engine:
            self._engine.quit()
            self._engine = None

    def get_best_move(
        self,
        fen: str,
        difficulty: BotDifficulty = BotDifficulty.MEDIUM,
    ) -> str:
        """
        Get the best move for the given position at the specified difficulty.

        Args:
            fen: The current board position in FEN notation
            difficulty: The difficulty level for the bot

        Returns:
            The best move in UCI notation (e.g., "e2e4")
        """
        engine = self._get_engine()
        board = chess.Board(fen)

        settings = DIFFICULTY_SETTINGS[difficulty]

        # Configure engine for difficulty
        engine.configure({
            "Skill Level": settings["skill_level"],
        })

        # Try to set UCI_LimitStrength and UCI_Elo if supported
        try:
            engine.configure({
                "UCI_LimitStrength": True,
                "UCI_Elo": settings["elo"],
            })
        except chess.engine.EngineError:
            # Engine might not support these options
            pass

        # Get the best move
        result = engine.play(
            board,
            chess.engine.Limit(
                time=settings["time_limit"],
                depth=settings["depth"],
            ),
        )

        if result.move is None:
            raise RuntimeError("Engine returned no move")

        return result.move.uci()

    def analyze_position(
        self,
        fen: str,
        depth: int = 15,
    ) -> dict:
        """
        Analyze a position and return evaluation.

        Args:
            fen: The board position in FEN notation
            depth: Analysis depth

        Returns:
            Dictionary with score and best line
        """
        engine = self._get_engine()
        board = chess.Board(fen)

        info = engine.analyse(board, chess.engine.Limit(depth=depth))

        score = info.get("score")
        pv = info.get("pv", [])

        # Convert score to centipawns or mate
        if score:
            if score.is_mate():
                score_value = f"M{score.relative.mate()}"
            else:
                score_value = score.relative.score()
        else:
            score_value = 0

        return {
            "score": score_value,
            "best_line": [move.uci() for move in pv[:5]],
            "depth": info.get("depth", depth),
        }

    def is_available(self) -> bool:
        """Check if Stockfish is available."""
        try:
            engine = self._get_engine()
            return engine is not None
        except Exception:
            return False


# Global instance (lazy initialization)
_stockfish_service: Optional[StockfishService] = None


def get_stockfish_service() -> StockfishService:
    """Get the global Stockfish service instance."""
    global _stockfish_service
    if _stockfish_service is None:
        _stockfish_service = StockfishService()
    return _stockfish_service
