from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field


class ProjectCreate(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = None
    color: str | None = Field(default=None, max_length=7)
    weekly_goal_hours: float | None = None
    github_repo: str | None = Field(default=None, max_length=255)


class ProjectUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    color: str | None = Field(default=None, max_length=7)
    status: str | None = Field(default=None, max_length=20)
    weekly_goal_hours: float | None = None
    github_repo: str | None = Field(default=None, max_length=255)


class ProjectResponse(SQLModel):
    id: UUID
    name: str
    description: str | None
    color: str | None
    status: str
    weekly_goal_hours: float | None
    github_repo: str | None
    created_at: datetime
    updated_at: datetime
