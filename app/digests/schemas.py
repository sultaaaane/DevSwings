from datetime import datetime, date
from uuid import UUID
from typing import Dict, Any
from sqlmodel import SQLModel


class DigestResponse(SQLModel):
    id: UUID
    user_id: UUID
    period_start: date
    period_end: date
    content: Dict[str, Any]
    delivered_at: datetime | None
    created_at: datetime
