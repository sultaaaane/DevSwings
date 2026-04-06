from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.streaks.schemas import StreakResponse
from app.core.database import get_session
from app.auth.dependencies import get_current_user_id
from app.streaks import service as streak_service
from uuid import UUID

router = APIRouter()


@router.get("/me", response_model=StreakResponse)
def get_my_streak(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return streak_service.get_streak_status(UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
