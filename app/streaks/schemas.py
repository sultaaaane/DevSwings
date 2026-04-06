from datetime import date, datetime
from uuid import UUID
from sqlmodel import SQLModel


class StreakResponse(SQLModel):
    id: UUID
    user_id: UUID
    current_streak: int
    longest_streak: int
    last_active_date: date | None
    freeze_used: bool
    updated_at: datetime
