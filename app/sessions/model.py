from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class WorkSession(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    project_id: UUID | None = Field(default=None, foreign_key="projects.id")
    energy_start: int = Field(ge=1, le=10)
    energy_end: int | None = Field(default=None, ge=1, le=10)
    mood: str | None = Field(default=None, max_length=20)
    flow_achieved: bool = Field(default=False)
    notes: str | None = None
    blockers: str | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    duration_minutes: int | None = None
    status: str = Field(default="open", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
