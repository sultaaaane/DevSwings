from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.digests.schemas import DigestResponse
from app.core.database import get_session
from app.auth.dependencies import get_current_user_id
from app.digests import service as digest_service
from uuid import UUID

router = APIRouter()


@router.get("", response_model=list[DigestResponse])
def get_my_digests(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return digest_service.get_user_digests(UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{digest_id}", response_model=DigestResponse)
def get_digest(
    digest_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return digest_service.get_digest(digest_id, UUID(user_id), db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
