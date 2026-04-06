from datetime import datetime
from uuid import UUID
from typing import Dict, Any
from sqlmodel import SQLModel


class InsightResponse(SQLModel):
    id: UUID
    user_id: UUID
    project_id: UUID | None
    type: str
    value: Dict[str, Any]
    computed_at: datetime


class StatsSummary(SQLModel):
    total_sessions: int
    total_duration_minutes: int
    total_commits: int
    average_energy_start: float | None
    average_energy_end: float | None
    flow_sessions_count: int
