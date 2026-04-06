from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field


class SessionBase(SQLModel):
    project_id: UUID | None = Field(default=None)
    energy_start: int = Field(ge=1, le=10)
    mood: str | None = Field(default=None, max_length=20)
    notes: str | None = None
    blockers: str | None = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(SQLModel):
    energy_start: int | None = Field(default=None, ge=1, le=10)
    energy_end: int | None = Field(default=None, ge=1, le=10)
    mood: str | None = Field(default=None, max_length=20)
    flow_achieved: bool | None = Field(default=None)
    notes: str | None = None
    blockers: str | None = None
    status: str | None = Field(default=None, max_length=20)
    ended_at: datetime | None = None


class SessionResponse(SessionBase):
    id: UUID
    user_id: UUID
    energy_end: int | None
    flow_achieved: bool
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int | None
    status: str
    created_at: datetime


class SessionEnd(SQLModel):
    energy_end: int = Field(ge=1, le=10)
    flow_achieved: bool = Field(default=False)
    notes: str | None = None
    blockers: str | None = None
