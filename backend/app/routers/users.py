from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserResponse, StreakResponse
from app.services import UserService

router = APIRouter()


@router.post("/sync", response_model=UserResponse)
def sync_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Sync user from Discord OAuth.

    Creates a new user or updates existing user's info.
    Called after Discord login.
    """
    service = UserService(db)
    user = service.get_or_create_user(user_data)
    return user


@router.get("/{discord_id}", response_model=UserResponse)
def get_user(
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Get user by Discord ID."""
    service = UserService(db)
    user = service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/{discord_id}/streak", response_model=StreakResponse)
def get_streak(
    discord_id: str,
    db: Session = Depends(get_db),
):
    """Get user's streak information."""
    service = UserService(db)
    user = service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return service.get_streak(user)


@router.post("/{discord_id}/puzzles/{puzzle_id}/complete", response_model=StreakResponse)
def complete_puzzle(
    discord_id: str,
    puzzle_id: int,
    success: bool = True,
    db: Session = Depends(get_db),
):
    """
    Record puzzle completion for a user.

    Updates the user's streak if successful.
    """
    service = UserService(db)
    user = service.get_user_by_discord_id(discord_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return service.record_puzzle_completion(user, puzzle_id, success)
