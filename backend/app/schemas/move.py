from pydantic import BaseModel


class MoveRequest(BaseModel):
    move: str  # UCI format (e.g., "e2e4", "e7e8q")
    move_index: int  # Current move index in the solution


class MoveResponse(BaseModel):
    correct: bool
    is_complete: bool = False
    opponent_move: str | None = None  # Next opponent move if correct
    message: str | None = None
