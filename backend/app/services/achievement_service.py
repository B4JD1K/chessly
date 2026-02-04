"""
Achievement Service - zarządzanie achievementami użytkowników.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from app.models.achievement import Achievement, UserAchievement
from app.models.user import User
from app.services.event_service import GameEvent, EventService


class AchievementService:
    """Serwis do zarządzania achievementami"""

    @staticmethod
    def get_all_achievements(db: Session) -> list[Achievement]:
        """Pobiera wszystkie aktywne achievementy"""
        return db.query(Achievement).filter(
            Achievement.is_active == True
        ).order_by(Achievement.order_index).all()

    @staticmethod
    def get_user_achievements(db: Session, user_id: int) -> list[UserAchievement]:
        """Pobiera achievementy użytkownika"""
        return db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()

    @staticmethod
    def get_user_unlocked_achievement_ids(db: Session, user_id: int) -> set[int]:
        """Pobiera ID odblokowanych achievementów użytkownika"""
        results = db.query(UserAchievement.achievement_id).filter(
            UserAchievement.user_id == user_id
        ).all()
        return {r[0] for r in results}

    @staticmethod
    def has_achievement(db: Session, user_id: int, achievement_code: str) -> bool:
        """Sprawdza czy użytkownik ma dany achievement"""
        return db.query(UserAchievement).join(Achievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                Achievement.code == achievement_code
            )
        ).first() is not None

    @staticmethod
    def unlock_achievement(db: Session, user_id: int, achievement_id: int) -> Optional[UserAchievement]:
        """Odblokowuje achievement dla użytkownika"""
        # Check if already unlocked
        existing = db.query(UserAchievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id
            )
        ).first()

        if existing:
            return None  # Already unlocked

        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id
        )
        db.add(user_achievement)
        db.commit()
        db.refresh(user_achievement)
        return user_achievement

    @staticmethod
    def check_and_unlock_achievements(event: GameEvent, db: Session) -> list[Achievement]:
        """
        Sprawdza i odblokowuje achievementy na podstawie eventu.
        Zwraca listę nowo odblokowanych achievementów.
        """
        unlocked = []

        # Pobierz achievementy pasujące do typu eventu
        matching_achievements = db.query(Achievement).filter(
            and_(
                Achievement.event_type == event.event_type.value,
                Achievement.is_active == True
            )
        ).all()

        # Pobierz już odblokowane achievementy użytkownika
        unlocked_ids = AchievementService.get_user_unlocked_achievement_ids(db, event.user_id)

        for achievement in matching_achievements:
            # Skip if already unlocked
            if achievement.id in unlocked_ids:
                continue

            # Check threshold
            if event.value >= achievement.threshold:
                user_achievement = AchievementService.unlock_achievement(
                    db, event.user_id, achievement.id
                )
                if user_achievement:
                    unlocked.append(achievement)

        return unlocked

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """Pobiera statystyki użytkownika dla achievementów"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        return {
            "puzzles_solved": user.puzzles_solved,
            "lessons_completed": user.lessons_completed,
            "games_won": user.games_won,
            "current_streak": user.current_streak,
            "best_streak": user.best_streak,
        }


# Rejestracja handlera w EventService przy imporcie
def _achievement_event_handler(event: GameEvent, db: Session):
    """Handler eventów dla achievementów"""
    AchievementService.check_and_unlock_achievements(event, db)


EventService.register_handler(_achievement_event_handler)
