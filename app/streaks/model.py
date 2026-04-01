from datetime import datetime, date
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Streak(SQLModel, table=True):
    __tablename__ = "streaks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_active_date: date | None = None
    freeze_used: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
