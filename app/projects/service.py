from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from app.projects.model import Project
from app.projects.schemas import ProjectCreate, ProjectUpdate


def create_project(data: ProjectCreate, user_id: str, db: Session) -> Project:
    project = Project(**data.model_dump(), user_id=UUID(user_id))
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_projects(user_id: str, db: Session) -> list[Project]:
    return db.exec(select(Project).where(Project.user_id == UUID(user_id))).all()


def get_project(project_id: UUID, user_id: str, db: Session) -> Project:
    project = db.exec(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == UUID(user_id))
    ).first()

    if not project:
        raise ValueError("Project not found")

    return project


def update_project(
    project_id: UUID, data: ProjectUpdate, user_id: str, db: Session
) -> Project:
    project = get_project(project_id, user_id, db)

    # only update fields that were actually sent
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(project_id: UUID, user_id: str, db: Session) -> None:
    project = get_project(project_id, user_id, db)
    db.delete(project)
    db.commit()
