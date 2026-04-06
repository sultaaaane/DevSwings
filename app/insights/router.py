from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.insights.schemas import InsightResponse, StatsSummary
from app.core.database import get_session
from app.auth.dependencies import get_current_user_id
from app.insights import service as insight_service
from uuid import UUID

router = APIRouter()


@router.get("/me", response_model=StatsSummary)
def get_my_stats(
    project_id: UUID | None = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return insight_service.get_user_stats(UUID(user_id), db, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=list[InsightResponse])
def get_insights(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return insight_service.list_insights(UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
