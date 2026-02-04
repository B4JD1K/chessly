from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.lesson import LessonCategory
from app.models.user import User
from app.services.lesson_service import LessonService
from app.schemas.lesson import (
    LessonResponse,
    LessonDetailResponse,
    LessonStepResponse,
    LessonProgressResponse,
    LessonWithProgressResponse,
    ValidateLessonMoveRequest,
    ValidateLessonMoveResponse,
    CategoryProgressResponse,
)

router = APIRouter()


def get_user_by_discord_id(db: Session, discord_id: str) -> User:
    """Helper to get user by Discord ID"""
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/categories", response_model=list[str])
def get_categories():
    """Pobiera listę kategorii lekcji"""
    return [c.value for c in LessonCategory]


@router.get("", response_model=list[LessonResponse])
def get_lessons(
    category: Optional[LessonCategory] = None,
    db: Session = Depends(get_db)
):
    """Pobiera listę wszystkich lekcji"""
    lessons = LessonService.get_all_lessons(db, category)
    return [
        LessonResponse(
            id=lesson.id,
            title=lesson.title,
            description=lesson.description,
            category=lesson.category,
            level=lesson.level,
            order_index=lesson.order_index,
            steps_count=len(lesson.steps)
        )
        for lesson in lessons
    ]


@router.get("/with-progress", response_model=list[LessonWithProgressResponse])
def get_lessons_with_progress(
    discord_id: str,
    category: Optional[LessonCategory] = None,
    db: Session = Depends(get_db)
):
    """Pobiera listę lekcji z postępem użytkownika"""
    user = get_user_by_discord_id(db, discord_id)
    lessons = LessonService.get_all_lessons(db, category)
    progress_list = LessonService.get_user_all_progress(db, user.id)
    progress_map = {p.lesson_id: p for p in progress_list}

    result = []
    for lesson in lessons:
        lesson_response = LessonResponse(
            id=lesson.id,
            title=lesson.title,
            description=lesson.description,
            category=lesson.category,
            level=lesson.level,
            order_index=lesson.order_index,
            steps_count=len(lesson.steps)
        )

        progress = progress_map.get(lesson.id)
        progress_response = None
        if progress:
            progress_response = LessonProgressResponse(
                lesson_id=lesson.id,
                status=progress.status,
                current_step_index=progress.current_step_index,
                total_steps=len(lesson.steps),
                started_at=progress.started_at,
                completed_at=progress.completed_at
            )

        result.append(LessonWithProgressResponse(
            lesson=lesson_response,
            progress=progress_response
        ))

    return result


@router.get("/category-progress", response_model=list[CategoryProgressResponse])
def get_category_progress(
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Pobiera postęp użytkownika w kategoriach"""
    user = get_user_by_discord_id(db, discord_id)
    return LessonService.get_category_progress(db, user.id)


@router.get("/recommended", response_model=Optional[LessonResponse])
def get_recommended_lesson(
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Pobiera rekomendowaną lekcję dla użytkownika"""
    user = get_user_by_discord_id(db, discord_id)
    lesson = LessonService.get_recommended_lesson(db, user.id)

    if not lesson:
        return None

    return LessonResponse(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        category=lesson.category,
        level=lesson.level,
        order_index=lesson.order_index,
        steps_count=len(lesson.steps)
    )


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Pobiera szczegóły lekcji"""
    lesson = LessonService.get_lesson_with_steps(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return LessonDetailResponse(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        category=lesson.category,
        level=lesson.level,
        steps=[
            LessonStepResponse(
                id=step.id,
                order_index=step.order_index,
                instruction=step.instruction,
                hint=step.hint,
                fen=step.fen
            )
            for step in lesson.steps
        ]
    )


@router.get("/{lesson_id}/progress", response_model=LessonProgressResponse)
def get_lesson_progress(
    lesson_id: int,
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Pobiera postęp użytkownika w lekcji"""
    user = get_user_by_discord_id(db, discord_id)
    lesson = LessonService.get_lesson_with_steps(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = LessonService.get_user_progress(db, user.id, lesson_id)

    if not progress:
        from app.models.user_lesson_progress import LessonStatus
        return LessonProgressResponse(
            lesson_id=lesson_id,
            status=LessonStatus.NOT_STARTED,
            current_step_index=0,
            total_steps=len(lesson.steps),
            started_at=None,
            completed_at=None
        )

    return LessonProgressResponse(
        lesson_id=lesson_id,
        status=progress.status,
        current_step_index=progress.current_step_index,
        total_steps=len(lesson.steps),
        started_at=progress.started_at,
        completed_at=progress.completed_at
    )


@router.post("/{lesson_id}/start", response_model=LessonProgressResponse)
def start_lesson(
    lesson_id: int,
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Rozpoczyna lekcję dla użytkownika"""
    user = get_user_by_discord_id(db, discord_id)
    lesson = LessonService.get_lesson_with_steps(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = LessonService.start_lesson(db, user.id, lesson_id)

    return LessonProgressResponse(
        lesson_id=lesson_id,
        status=progress.status,
        current_step_index=progress.current_step_index,
        total_steps=len(lesson.steps),
        started_at=progress.started_at,
        completed_at=progress.completed_at
    )


@router.post("/{lesson_id}/validate-move", response_model=ValidateLessonMoveResponse)
def validate_lesson_move(
    lesson_id: int,
    request: ValidateLessonMoveRequest,
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Waliduje ruch użytkownika w lekcji"""
    user = get_user_by_discord_id(db, discord_id)

    result = LessonService.validate_move(
        db=db,
        user_id=user.id,
        lesson_id=lesson_id,
        move_uci=request.move
    )

    return ValidateLessonMoveResponse(**result)


@router.get("/{lesson_id}/steps/{step_index}", response_model=LessonStepResponse)
def get_lesson_step(
    lesson_id: int,
    step_index: int,
    db: Session = Depends(get_db)
):
    """Pobiera konkretny krok lekcji"""
    step = LessonService.get_step(db, lesson_id, step_index)

    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    return LessonStepResponse(
        id=step.id,
        order_index=step.order_index,
        instruction=step.instruction,
        hint=step.hint,
        fen=step.fen
    )
