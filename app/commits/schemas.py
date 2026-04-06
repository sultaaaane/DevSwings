from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field


class CommitBase(SQLModel):
    sha: str = Field(max_length=40)
    message: str
    repo_name: str = Field(max_length=255)
    additions: int = Field(default=0)
    deletions: int = Field(default=0)
    committed_at: datetime
    session_id: UUID | None = None
    project_id: UUID | None = None


class CommitCreate(CommitBase):
    pass


class CommitResponse(CommitBase):
    id: UUID
    user_id: UUID
    received_at: datetime
