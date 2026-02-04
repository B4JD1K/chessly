"""
Lesson Service - zarządzanie lekcjami i postępem użytkownika.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from typing import Optional
import chess

from app.models.lesson import Lesson, LessonStep, LessonCategory, LessonLevel
from app.models.user_lesson_progress import UserLessonProgress, LessonStatus
from app.models.user import User
from app.services.event_service import EventService


class LessonService:
    """Serwis do zarządzania lekcjami"""

    @staticmethod
    def get_all_lessons(db: Session, category: Optional[LessonCategory] = None) -> list[Lesson]:
        """Pobiera wszystkie opublikowane lekcje"""
        query = db.query(Lesson).filter(Lesson.is_published == True)
        if category:
            query = query.filter(Lesson.category == category)
        return query.order_by(Lesson.category, Lesson.order_index).all()

    @staticmethod
    def get_lesson(db: Session, lesson_id: int) -> Optional[Lesson]:
        """Pobiera lekcję po ID"""
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()

    @staticmethod
    def get_lesson_with_steps(db: Session, lesson_id: int) -> Optional[Lesson]:
        """Pobiera lekcję wraz z krokami"""
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if lesson:
            # Eager load steps
            _ = lesson.steps
        return lesson

    @staticmethod
    def get_step(db: Session, lesson_id: int, step_index: int) -> Optional[LessonStep]:
        """Pobiera konkretny krok lekcji"""
        return db.query(LessonStep).filter(
            and_(
                LessonStep.lesson_id == lesson_id,
                LessonStep.order_index == step_index
            )
        ).first()

    @staticmethod
    def get_user_progress(db: Session, user_id: int, lesson_id: int) -> Optional[UserLessonProgress]:
        """Pobiera postęp użytkownika w lekcji"""
        return db.query(UserLessonProgress).filter(
            and_(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.lesson_id == lesson_id
            )
        ).first()

    @staticmethod
    def get_user_all_progress(db: Session, user_id: int) -> list[UserLessonProgress]:
        """Pobiera cały postęp użytkownika"""
        return db.query(UserLessonProgress).filter(
            UserLessonProgress.user_id == user_id
        ).all()

    @staticmethod
    def start_lesson(db: Session, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Rozpoczyna lekcję dla użytkownika"""
        progress = LessonService.get_user_progress(db, user_id, lesson_id)

        if progress:
            if progress.status == LessonStatus.COMPLETED:
                # Reset dla ponownego przejścia
                progress.status = LessonStatus.IN_PROGRESS
                progress.current_step_index = 0
                progress.started_at = datetime.utcnow()
                progress.completed_at = None
            return progress

        progress = UserLessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status=LessonStatus.IN_PROGRESS,
            current_step_index=0,
            started_at=datetime.utcnow()
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def validate_move(
        db: Session,
        user_id: int,
        lesson_id: int,
        move_uci: str
    ) -> dict:
        """
        Waliduje ruch użytkownika w kroku lekcji.
        Zwraca dict z informacjami o wyniku.
        """
        lesson = LessonService.get_lesson_with_steps(db, lesson_id)
        if not lesson:
            return {"correct": False, "message": "Lesson not found"}

        progress = LessonService.get_user_progress(db, user_id, lesson_id)
        if not progress:
            progress = LessonService.start_lesson(db, user_id, lesson_id)

        current_step = LessonService.get_step(db, lesson_id, progress.current_step_index)
        if not current_step:
            return {"correct": False, "message": "Step not found"}

        # Sprawdź czy ruch jest legalny
        try:
            board = chess.Board(current_step.fen)
            move = chess.Move.from_uci(move_uci)
            if move not in board.legal_moves:
                return {
                    "correct": False,
                    "is_step_complete": False,
                    "is_lesson_complete": False,
                    "message": "Illegal move"
                }
        except (ValueError, chess.InvalidMoveError):
            return {
                "correct": False,
                "is_step_complete": False,
                "is_lesson_complete": False,
                "message": "Invalid move format"
            }

        # Sprawdź czy ruch jest oczekiwany
        expected_moves = [m.strip() for m in current_step.expected_moves.split(",")]
        is_correct = move_uci in expected_moves

        if not is_correct:
            return {
                "correct": False,
                "is_step_complete": False,
                "is_lesson_complete": False,
                "message": current_step.hint or "Try again"
            }

        # Ruch poprawny - wykonaj go na planszy
        board.push(move)
        fen_after = board.fen()

        # Sprawdź czy jest ruch przeciwnika
        opponent_move = None
        if current_step.opponent_move:
            try:
                opp_move = chess.Move.from_uci(current_step.opponent_move)
                if opp_move in board.legal_moves:
                    board.push(opp_move)
                    fen_after = current_step.fen_after_opponent or board.fen()
                    opponent_move = current_step.opponent_move
            except (ValueError, chess.InvalidMoveError):
                pass

        # Przejdź do następnego kroku
        total_steps = len(lesson.steps)
        next_step_index = progress.current_step_index + 1
        is_lesson_complete = next_step_index >= total_steps

        if is_lesson_complete:
            progress.status = LessonStatus.COMPLETED
            progress.completed_at = datetime.utcnow()

            # Update user stats
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.lessons_completed += 1

                # Emit event
                EventService.emit_lesson_completed(
                    user_id=user_id,
                    lesson_count=user.lessons_completed,
                    db=db,
                    category=lesson.category.value
                )

                # Check if category is completed
                LessonService._check_category_completion(db, user_id, lesson.category)
        else:
            progress.current_step_index = next_step_index

        db.commit()

        return {
            "correct": True,
            "is_step_complete": True,
            "is_lesson_complete": is_lesson_complete,
            "next_step_index": None if is_lesson_complete else next_step_index,
            "opponent_move": opponent_move,
            "fen_after": fen_after,
            "message": "Correct!" if not is_lesson_complete else "Lesson completed!"
        }

    @staticmethod
    def _check_category_completion(db: Session, user_id: int, category: LessonCategory):
        """Sprawdza czy użytkownik ukończył wszystkie lekcje w kategorii"""
        # Pobierz wszystkie lekcje w kategorii
        total_in_category = db.query(func.count(Lesson.id)).filter(
            and_(
                Lesson.category == category,
                Lesson.is_published == True
            )
        ).scalar()

        # Pobierz ukończone lekcje użytkownika w kategorii
        completed_in_category = db.query(func.count(UserLessonProgress.id)).join(Lesson).filter(
            and_(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.status == LessonStatus.COMPLETED,
                Lesson.category == category
            )
        ).scalar()

        if completed_in_category >= total_in_category and total_in_category > 0:
            EventService.emit_category_completed(user_id, category.value, db)

    @staticmethod
    def get_category_progress(db: Session, user_id: int) -> list[dict]:
        """Pobiera postęp użytkownika w każdej kategorii"""
        result = []

        for category in LessonCategory:
            total = db.query(func.count(Lesson.id)).filter(
                and_(
                    Lesson.category == category,
                    Lesson.is_published == True
                )
            ).scalar()

            completed = db.query(func.count(UserLessonProgress.id)).join(Lesson).filter(
                and_(
                    UserLessonProgress.user_id == user_id,
                    UserLessonProgress.status == LessonStatus.COMPLETED,
                    Lesson.category == category
                )
            ).scalar()

            in_progress = db.query(func.count(UserLessonProgress.id)).join(Lesson).filter(
                and_(
                    UserLessonProgress.user_id == user_id,
                    UserLessonProgress.status == LessonStatus.IN_PROGRESS,
                    Lesson.category == category
                )
            ).scalar()

            result.append({
                "category": category,
                "total_lessons": total,
                "completed_lessons": completed,
                "in_progress_lessons": in_progress
            })

        return result

    @staticmethod
    def get_recommended_lesson(db: Session, user_id: int) -> Optional[Lesson]:
        """Pobiera rekomendowaną lekcję dla użytkownika (pierwszą nieukończoną)"""
        # Pobierz ukończone lekcje
        completed_ids = db.query(UserLessonProgress.lesson_id).filter(
            and_(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.status == LessonStatus.COMPLETED
            )
        ).subquery()

        # Pobierz pierwszą nieukończoną lekcję
        lesson = db.query(Lesson).filter(
            and_(
                Lesson.is_published == True,
                ~Lesson.id.in_(completed_ids)
            )
        ).order_by(
            Lesson.level,  # Beginner first
            Lesson.category,
            Lesson.order_index
        ).first()

        return lesson
