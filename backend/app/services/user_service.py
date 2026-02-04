from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import User, UserPuzzleProgress, PuzzleStatus
from app.schemas import UserCreate, StreakResponse
from app.services.event_service import EventService


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, user_data: UserCreate) -> User:
        """Get existing user or create new one by Discord ID."""
        user = (
            self.db.query(User)
            .filter(User.discord_id == user_data.discord_id)
            .first()
        )

        if user:
            # Update username and avatar if changed
            user.username = user_data.username
            user.avatar_url = user_data.avatar_url
            self.db.commit()
            return user

        user = User(
            discord_id=user_data.discord_id,
            username=user_data.username,
            avatar_url=user_data.avatar_url,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_discord_id(self, discord_id: str) -> User | None:
        """Get user by Discord ID."""
        return (
            self.db.query(User)
            .filter(User.discord_id == discord_id)
            .first()
        )

    def get_streak(self, user: User) -> StreakResponse:
        """Get user's streak information."""
        today = date.today()
        puzzle_solved_today = user.last_puzzle_date == today

        return StreakResponse(
            current_streak=user.current_streak,
            best_streak=user.best_streak,
            last_puzzle_date=user.last_puzzle_date,
            puzzle_solved_today=puzzle_solved_today,
        )

    def record_puzzle_completion(
        self, user: User, puzzle_id: int, success: bool
    ) -> StreakResponse:
        """Record puzzle completion and update streak."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Check if already completed today
        existing_progress = (
            self.db.query(UserPuzzleProgress)
            .filter(
                UserPuzzleProgress.user_id == user.id,
                UserPuzzleProgress.puzzle_id == puzzle_id,
                UserPuzzleProgress.status == PuzzleStatus.SOLVED.value,
            )
            .first()
        )

        if existing_progress:
            return self.get_streak(user)

        # Record progress
        progress = (
            self.db.query(UserPuzzleProgress)
            .filter(
                UserPuzzleProgress.user_id == user.id,
                UserPuzzleProgress.puzzle_id == puzzle_id,
            )
            .first()
        )

        if not progress:
            progress = UserPuzzleProgress(
                user_id=user.id,
                puzzle_id=puzzle_id,
            )
            self.db.add(progress)

        progress.attempts += 1

        if success:
            progress.status = PuzzleStatus.SOLVED.value
            from datetime import datetime
            progress.completed_at = datetime.now()

            # Update user stats
            user.puzzles_solved += 1

            # Update streak
            if user.last_puzzle_date == yesterday:
                user.current_streak += 1
            elif user.last_puzzle_date != today:
                user.current_streak = 1

            user.last_puzzle_date = today

            if user.current_streak > user.best_streak:
                user.best_streak = user.current_streak

            self.db.commit()

            # Emit events for achievements
            EventService.emit_puzzle_solved(
                user_id=user.id,
                puzzle_count=user.puzzles_solved,
                db=self.db
            )

            EventService.emit_streak_day(
                user_id=user.id,
                streak_days=user.current_streak,
                db=self.db
            )
        else:
            self.db.commit()

        return self.get_streak(user)
