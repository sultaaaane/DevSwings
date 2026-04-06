from uuid import UUID
from sqlmodel import Session, select
from app.commits.model import Commit
from app.commits.schemas import CommitCreate


def create_commit(data: CommitCreate, user_id: UUID, db: Session) -> Commit:
    commit = Commit(**data.model_dump(), user_id=user_id)
    db.add(commit)
    db.commit()
    db.refresh(commit)
    return commit


def get_commits(
    user_id: UUID, db: Session, project_id: UUID | None = None
) -> list[Commit]:
    statement = select(Commit).where(Commit.user_id == user_id)
    if project_id:
        statement = statement.where(Commit.project_id == project_id)
    return db.exec(statement).all()


def batch_create_commits(
    data: list[CommitCreate], user_id: UUID, db: Session
) -> list[Commit]:
    created_commits = []
    for commit_data in data:
        # Avoid duplicate SHAs
        existing = db.exec(select(Commit).where(Commit.sha == commit_data.sha)).first()
        if existing:
            continue
        commit = Commit(**commit_data.model_dump(), user_id=user_id)
        db.add(commit)
        created_commits.append(commit)
    db.commit()
    for c in created_commits:
        db.refresh(c)
    return created_commits
