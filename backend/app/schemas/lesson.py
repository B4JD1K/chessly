from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models.lesson import LessonCategory, LessonLevel
from app.models.user_lesson_progress import LessonStatus


class LessonStepResponse(BaseModel):
    id: int
    order_index: int
    instruction: str
    hint: Optional[str] = None
    fen: str

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: LessonCategory
    level: LessonLevel
    order_index: int
    steps_count: int

    class Config:
        from_attributes = True


class LessonDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: LessonCategory
    level: LessonLevel
    steps: list[LessonStepResponse]

    class Config:
        from_attributes = True


class LessonProgressResponse(BaseModel):
    lesson_id: int
    status: LessonStatus
    current_step_index: int
    total_steps: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LessonWithProgressResponse(BaseModel):
    lesson: LessonResponse
    progress: Optional[LessonProgressResponse] = None

    class Config:
        from_attributes = True


class ValidateLessonMoveRequest(BaseModel):
    move: str  # Ruch w notacji UCI (np. "e2e4")


class ValidateLessonMoveResponse(BaseModel):
    correct: bool
    is_step_complete: bool
    is_lesson_complete: bool
    next_step_index: Optional[int] = None
    opponent_move: Optional[str] = None  # Ruch przeciwnika w UCI
    fen_after: Optional[str] = None  # FEN po ruchu (i opcjonalnie po ruchu przeciwnika)
    message: Optional[str] = None


class CategoryProgressResponse(BaseModel):
    category: LessonCategory
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
