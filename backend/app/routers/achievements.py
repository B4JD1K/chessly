from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.achievement_service import AchievementService
from app.schemas.achievement import (
    AchievementResponse,
    UserAchievementResponse,
    UserAchievementsListResponse,
)

router = APIRouter()


def get_user_by_discord_id(db: Session, discord_id: str) -> User:
    """Helper to get user by Discord ID"""
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[AchievementResponse])
def get_all_achievements(db: Session = Depends(get_db)):
    """Pobiera listę wszystkich achievementów"""
    achievements = AchievementService.get_all_achievements(db)
    return [
        AchievementResponse(
            id=a.id,
            code=a.code,
            name=a.name,
            description=a.description,
            icon=a.icon,
            threshold=a.threshold
        )
        for a in achievements
    ]


@router.get("/user/{discord_id}", response_model=UserAchievementsListResponse)
def get_user_achievements(
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Pobiera achievementy użytkownika (odblokowane i zablokowane)"""
    user = get_user_by_discord_id(db, discord_id)

    all_achievements = AchievementService.get_all_achievements(db)
    user_achievements = AchievementService.get_user_achievements(db, user.id)

    unlocked_ids = {ua.achievement_id for ua in user_achievements}

    unlocked = []
    locked = []

    for ua in user_achievements:
        unlocked.append(UserAchievementResponse(
            achievement=AchievementResponse(
                id=ua.achievement.id,
                code=ua.achievement.code,
                name=ua.achievement.name,
                description=ua.achievement.description,
                icon=ua.achievement.icon,
                threshold=ua.achievement.threshold
            ),
            unlocked_at=ua.unlocked_at
        ))

    for a in all_achievements:
        if a.id not in unlocked_ids:
            locked.append(AchievementResponse(
                id=a.id,
                code=a.code,
                name=a.name,
                description=a.description,
                icon=a.icon,
                threshold=a.threshold
            ))

    return UserAchievementsListResponse(
        unlocked=unlocked,
        locked=locked,
        total_unlocked=len(unlocked),
        total_available=len(all_achievements)
    )


@router.get("/user/{discord_id}/stats")
def get_user_stats(
    discord_id: str,
    db: Session = Depends(get_db)
):
    """Pobiera statystyki użytkownika dla achievementów"""
    user = get_user_by_discord_id(db, discord_id)
    return AchievementService.get_user_stats(db, user.id)
