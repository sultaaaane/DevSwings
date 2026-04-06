from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column


class Insight(SQLModel, table=True):
    __tablename__ = "insights"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    project_id: UUID | None = Field(default=None, foreign_key="projects.id")
    type: str = Field(max_length=50)
    value: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    computed_at: datetime = Field(default_factory=datetime.utcnow)
