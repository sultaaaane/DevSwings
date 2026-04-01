from datetime import datetime, date
from uuid import UUID, uuid4
from typing import Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Digest(SQLModel, table=True):
    __tablename__ = "digests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    period_start: date
    period_end: date
    content: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    delivered_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)