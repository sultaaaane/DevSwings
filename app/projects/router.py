from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.projects.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.database import get_session
from app.auth.dependencies import get_current_user_id
from app.projects import service as project_service
from uuid import UUID

router = APIRouter()


@router.post("", response_model=ProjectResponse)
def create_project(
    data: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        return project_service.create_project(data, user_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProjectResponse])
def get_projects(
    user_id: str = Depends(get_current_user_id), db: Session = Depends(get_session)
):
    try:
        return project_service.get_projects(user_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        project = project_service.get_project(project_id, user_id, db)
        return project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        project = project_service.update_project(project_id, data, user_id, db)
        return project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_session),
):
    try:
        project_service.delete_project(project_id, user_id, db)
        return {"message": "Project deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
