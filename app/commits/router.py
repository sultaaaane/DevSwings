from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.commits.schemas import CommitCreate, CommitResponse
from app.core.database import get_session
from app.auth.dependencies import get_current_user_id
from app.commits import service as commit_service
from uuid import UUID

router = APIRouter()


@router.post("", response_model=CommitResponse)
def create_commit(
    data: CommitCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return commit_service.create_commit(data, UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=list[CommitResponse])
def batch_create_commits(
    data: list[CommitCreate],
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return commit_service.batch_create_commits(data, UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[CommitResponse])
def get_commits(
    project_id: UUID | None = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return commit_service.get_commits(UUID(user_id), db, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
