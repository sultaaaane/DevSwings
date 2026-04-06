from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as SQLSession
from app.sessions.schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionEnd,
)
from app.core.database import get_session as get_db_session
from app.auth.dependencies import get_current_user_id
from app.sessions import service as session_service
from uuid import UUID

router = APIRouter()


@router.post("", response_model=SessionResponse)
def create_session(
    data: SessionCreate,
    user_id: str = Depends(get_current_user_id),
    db: SQLSession = Depends(get_db_session),
):
    try:
        return session_service.create_session(data, UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[SessionResponse])
def get_sessions(
    user_id: str = Depends(get_current_user_id),
    db: SQLSession = Depends(get_db_session),
):
    try:
        return session_service.get_sessions(UUID(user_id), db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: SQLSession = Depends(get_db_session),
):
    try:
        return session_service.get_session(session_id, UUID(user_id), db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(
    session_id: UUID,
    data: SessionEnd,
    user_id: str = Depends(get_current_user_id),
    db: SQLSession = Depends(get_db_session),
):
    try:
        return session_service.end_session(session_id, data, UUID(user_id), db)
    except ValueError as e:
        if "already closed" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{session_id}", response_model=SessionResponse)
@router.patch("/{session_id}", response_model=SessionResponse)
@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: UUID,
    data: SessionUpdate,
    user_id: str = Depends(get_current_user_id),
    db: SQLSession = Depends(get_db_session),
):
    try:
        return session_service.update_session(session_id, data, UUID(user_id), db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{session_id}")
def delete_session(
    session_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: SQLSession = Depends(get_db_session),
):
    try:
        session_service.delete_session(session_id, UUID(user_id), db)
        return {"message": "Session deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
