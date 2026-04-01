from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Commit(SQLModel, table=True):
    __tablename__ = "commits"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    session_id: UUID | None = Field(default=None, foreign_key="sessions.id")
    project_id: UUID | None = Field(default=None, foreign_key="projects.id")
    sha: str = Field(unique=True, max_length=40)
    message: str
    repo_name: str = Field(max_length=255)
    additions: int = Field(default=0)
    deletions: int = Field(default=0)
    committed_at: datetime
    received_at: datetime = Field(default_factory=datetime.utcnow)