from datetime import date, datetime, timedelta
from uuid import UUID
from sqlmodel import Session, select
from app.streaks.model import Streak


def get_or_create_streak(user_id: UUID, db: Session) -> Streak:
    streak = db.exec(select(Streak).where(Streak.user_id == user_id)).first()
    if not streak:
        streak = Streak(user_id=user_id)
        db.add(streak)
        db.commit()
        db.refresh(streak)
    return streak


def update_user_streak(
    user_id: UUID, db: Session, activity_date: date | None = None
) -> Streak:
    if activity_date is None:
        activity_date = date.today()

    streak = get_or_create_streak(user_id, db)

    # If already updated today, do nothing
    if streak.last_active_date == activity_date:
        return streak

    # check if streak is continued (yesterday or today)
    yesterday = activity_date - timedelta(days=1)

    if streak.last_active_date == yesterday:
        streak.current_streak += 1
    elif (
        streak.last_active_date is None
        or (activity_date - streak.last_active_date).days > 1
    ):
        # streak broken or first activity
        streak.current_streak = 1
    else:
        # This case handles if activity is somehow logged for a past date but not yesterday
        pass

    # update longest streak
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    streak.last_active_date = activity_date
    streak.updated_at = datetime.utcnow()

    db.add(streak)
    db.commit()
    db.refresh(streak)
    return streak


def get_streak_status(user_id: UUID, db: Session) -> Streak:
    return get_or_create_streak(user_id, db)
