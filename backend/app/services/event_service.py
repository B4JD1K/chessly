"""
Event Service - centralny system zdarzeń dla achievementów.

Eventy:
- PUZZLE_SOLVED - użytkownik rozwiązał puzzle
- LESSON_COMPLETED - użytkownik ukończył lekcję
- STREAK_DAY - użytkownik osiągnął streak X dni
- GAME_WON - użytkownik wygrał grę
- CHECKMATE_DELIVERED - użytkownik dał mata
- CATEGORY_COMPLETED_BASICS - użytkownik ukończył wszystkie lekcje z kategorii basics
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any
from sqlalchemy.orm import Session


class EventType(str, Enum):
    PUZZLE_SOLVED = "PUZZLE_SOLVED"
    LESSON_COMPLETED = "LESSON_COMPLETED"
    STREAK_DAY = "STREAK_DAY"
    GAME_WON = "GAME_WON"
    CHECKMATE_DELIVERED = "CHECKMATE_DELIVERED"
    CATEGORY_COMPLETED_BASICS = "CATEGORY_COMPLETED_BASICS"
    CATEGORY_COMPLETED_TACTICS = "CATEGORY_COMPLETED_TACTICS"
    CATEGORY_COMPLETED_OPENINGS = "CATEGORY_COMPLETED_OPENINGS"
    CATEGORY_COMPLETED_ENDGAMES = "CATEGORY_COMPLETED_ENDGAMES"


@dataclass
class GameEvent:
    """Reprezentuje zdarzenie w grze"""
    event_type: EventType
    user_id: int
    value: int = 1  # Wartość eventu (np. liczba dni streaka, liczba puzzli)
    metadata: Optional[dict] = None


class EventService:
    """Serwis do emisji i obsługi eventów"""

    _handlers: list[Callable[[GameEvent, Session], Any]] = []

    @classmethod
    def register_handler(cls, handler: Callable[[GameEvent, Session], Any]):
        """Rejestruje handler eventów (np. AchievementService)"""
        cls._handlers.append(handler)

    @classmethod
    def emit(cls, event: GameEvent, db: Session):
        """Emituje event do wszystkich zarejestrowanych handlerów"""
        for handler in cls._handlers:
            try:
                handler(event, db)
            except Exception as e:
                # Log error but don't break the flow
                print(f"Error in event handler: {e}")

    @classmethod
    def emit_puzzle_solved(cls, user_id: int, puzzle_count: int, db: Session):
        """Emituje event rozwiązania puzzla"""
        event = GameEvent(
            event_type=EventType.PUZZLE_SOLVED,
            user_id=user_id,
            value=puzzle_count
        )
        cls.emit(event, db)

    @classmethod
    def emit_lesson_completed(cls, user_id: int, lesson_count: int, db: Session, category: str = None):
        """Emituje event ukończenia lekcji"""
        event = GameEvent(
            event_type=EventType.LESSON_COMPLETED,
            user_id=user_id,
            value=lesson_count,
            metadata={"category": category} if category else None
        )
        cls.emit(event, db)

    @classmethod
    def emit_streak_day(cls, user_id: int, streak_days: int, db: Session):
        """Emituje event streaka"""
        event = GameEvent(
            event_type=EventType.STREAK_DAY,
            user_id=user_id,
            value=streak_days
        )
        cls.emit(event, db)

    @classmethod
    def emit_game_won(cls, user_id: int, wins_count: int, db: Session):
        """Emituje event wygranej gry"""
        event = GameEvent(
            event_type=EventType.GAME_WON,
            user_id=user_id,
            value=wins_count
        )
        cls.emit(event, db)

    @classmethod
    def emit_checkmate(cls, user_id: int, db: Session):
        """Emituje event dania mata"""
        event = GameEvent(
            event_type=EventType.CHECKMATE_DELIVERED,
            user_id=user_id,
            value=1
        )
        cls.emit(event, db)

    @classmethod
    def emit_category_completed(cls, user_id: int, category: str, db: Session):
        """Emituje event ukończenia kategorii lekcji"""
        event_type_map = {
            "basics": EventType.CATEGORY_COMPLETED_BASICS,
            "tactics": EventType.CATEGORY_COMPLETED_TACTICS,
            "openings": EventType.CATEGORY_COMPLETED_OPENINGS,
            "endgames": EventType.CATEGORY_COMPLETED_ENDGAMES,
        }
        event_type = event_type_map.get(category)
        if event_type:
            event = GameEvent(
                event_type=event_type,
                user_id=user_id,
                value=1
            )
            cls.emit(event, db)
