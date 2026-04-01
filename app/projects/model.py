from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    name: str = Field(max_length=255)
    description: str | None = None
    color: str | None = Field(default=None, max_length=7)
    status: str = Field(default="active", max_length=20)
    weekly_goal_hours: float | None = None
    github_repo: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)