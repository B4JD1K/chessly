from datetime import date
import random

import chess
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Puzzle
from app.schemas import MoveRequest, MoveResponse


class PuzzleService:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_puzzle(self, puzzle_date: date | None = None) -> Puzzle | None:
        """Get a random daily puzzle for a given date, or today if not specified."""
        if puzzle_date is None:
            puzzle_date = date.today()

        # Get all puzzles for this date
        puzzles = (
            self.db.query(Puzzle)
            .filter(Puzzle.daily_date == puzzle_date)
            .all()
        )

        if not puzzles:
            return None

        # Return random one
        return random.choice(puzzles)

    def get_daily_puzzles(self, puzzle_date: date | None = None) -> list[Puzzle]:
        """Get all daily puzzles for a given date, or today if not specified."""
        if puzzle_date is None:
            puzzle_date = date.today()

        return (
            self.db.query(Puzzle)
            .filter(Puzzle.daily_date == puzzle_date)
            .all()
        )

    def get_puzzle_by_id(self, puzzle_id: int) -> Puzzle | None:
        """Get a puzzle by its ID."""
        return self.db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()

    def validate_move(
        self, puzzle: Puzzle, request: MoveRequest
    ) -> MoveResponse:
        """
        Validate a player's move against the puzzle solution.

        The puzzle solution contains alternating moves:
        - Odd indices (0, 2, 4, ...): Player moves
        - Even indices (1, 3, 5, ...): Opponent responses

        The FEN position is the state after the opponent's "setup" move,
        so the player moves first from this position.
        """
        solution_moves = puzzle.solution_moves

        # Check if move_index is valid
        if request.move_index < 0 or request.move_index >= len(solution_moves):
            return MoveResponse(
                correct=False,
                message="Invalid move index"
            )

        # Verify the move is for the player (even indices in solution)
        if request.move_index % 2 != 0:
            return MoveResponse(
                correct=False,
                message="Not player's turn"
            )

        # Build the board position up to the current move
        board = chess.Board(puzzle.fen)
        for i in range(request.move_index):
            move = chess.Move.from_uci(solution_moves[i])
            board.push(move)

        # Validate the move is legal
        try:
            player_move = chess.Move.from_uci(request.move)
        except ValueError:
            return MoveResponse(
                correct=False,
                message="Invalid move format"
            )

        if player_move not in board.legal_moves:
            return MoveResponse(
                correct=False,
                message="Illegal move"
            )

        # Check if move matches the solution
        expected_move = solution_moves[request.move_index]
        if request.move != expected_move:
            return MoveResponse(
                correct=False,
                message="Incorrect move"
            )

        # Move is correct - apply it
        board.push(player_move)

        # Check if puzzle is complete
        next_index = request.move_index + 1
        if next_index >= len(solution_moves):
            return MoveResponse(
                correct=True,
                is_complete=True,
                message="Puzzle solved!"
            )

        # Return the opponent's response move
        opponent_move = solution_moves[next_index]
        return MoveResponse(
            correct=True,
            is_complete=False,
            opponent_move=opponent_move
        )

    def create_puzzle(
        self,
        fen: str,
        solution: str,
        rating: int = 1500,
        themes: str | None = None,
        daily_date: date | None = None,
    ) -> Puzzle:
        """Create a new puzzle."""
        puzzle = Puzzle(
            fen=fen,
            solution=solution,
            rating=rating,
            themes=themes,
            daily_date=daily_date,
        )
        self.db.add(puzzle)
        self.db.commit()
        self.db.refresh(puzzle)
        return puzzle
