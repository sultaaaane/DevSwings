from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, max_length=255)
    password_hash: str | None = Field(default=None)
    github_id: str | None = Field(default=None, unique=True)
    github_username: str | None = Field(default=None)
    timezone: str = Field(default="UTC", max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
