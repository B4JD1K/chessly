from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PuzzleResponse, MoveRequest, MoveResponse
from app.services import PuzzleService

router = APIRouter()


@router.get("/daily", response_model=list[PuzzleResponse])
def get_daily_puzzles(
    puzzle_date: date | None = None,
    db: Session = Depends(get_db),
):
    """
    Get all daily puzzles for a given date.

    If no date is provided, returns today's puzzles.
    """
    service = PuzzleService(db)
    puzzles = service.get_daily_puzzles(puzzle_date)

    if not puzzles:
        raise HTTPException(
            status_code=404,
            detail="No puzzles available for this date"
        )

    return [PuzzleResponse.from_puzzle(p) for p in puzzles]


@router.get("/{puzzle_id}", response_model=PuzzleResponse)
def get_puzzle(
    puzzle_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific puzzle by ID."""
    service = PuzzleService(db)
    puzzle = service.get_puzzle_by_id(puzzle_id)

    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    return PuzzleResponse.from_puzzle(puzzle)


@router.post("/{puzzle_id}/validate-move", response_model=MoveResponse)
def validate_move(
    puzzle_id: int,
    request: MoveRequest,
    db: Session = Depends(get_db),
):
    """
    Validate a move for a puzzle.

    The move should be in UCI format (e.g., "e2e4", "e7e8q").
    The move_index indicates which move in the sequence this is (0-indexed).
    """
    service = PuzzleService(db)
    puzzle = service.get_puzzle_by_id(puzzle_id)

    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    return service.validate_move(puzzle, request)
