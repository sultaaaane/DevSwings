from uuid import UUID
from datetime import datetime
from uuid import UUID
from datetime import datetime
from sqlmodel import Session as SQLSession, select
from app.sessions.model import WorkSession as WorkSessionModel
from app.sessions.schemas import SessionCreate, SessionUpdate, SessionEnd
from app.streaks import service as streak_service


def create_session(
    data: SessionCreate, user_id: UUID, db: SQLSession
) -> WorkSessionModel:
    # Check for already active sessions (status is "open" in this model)
    active_session_statement = select(WorkSessionModel).where(
        WorkSessionModel.user_id == user_id, WorkSessionModel.status == "open"
    )
    active_session = db.exec(active_session_statement).first()
    if active_session:
        raise ValueError("User already has an active session.")

    new_session = WorkSessionModel(**data.model_dump(), user_id=user_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Update streak when a new session starts
    streak_service.update_user_streak(
        user_id, db, activity_date=new_session.started_at.date()
    )

    return new_session


def get_sessions(user_id: UUID, db: SQLSession) -> list[WorkSessionModel]:
    return list(
        db.exec(
            select(WorkSessionModel).where(WorkSessionModel.user_id == user_id)
        ).all()
    )


def get_session(session_id: UUID, user_id: UUID, db: SQLSession) -> WorkSessionModel:
    statement = select(WorkSessionModel).where(WorkSessionModel.id == session_id)
    result = db.exec(statement).first()
    if not result or result.user_id != user_id:
        raise ValueError("Session not found")
    return result


def update_session(
    session_id: UUID, data: SessionUpdate, user_id: UUID, db: SQLSession
) -> WorkSessionModel:
    existing_session = get_session(session_id, user_id, db)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(existing_session, field, value)
    db.add(existing_session)
    db.commit()
    db.refresh(existing_session)
    return existing_session


def end_session(
    session_id: UUID, data: SessionEnd, user_id: UUID, db: SQLSession
) -> WorkSessionModel:
    existing_session = get_session(session_id, user_id, db)
    if existing_session.status == "closed":
        raise ValueError("Session already closed")

    existing_session.energy_end = data.energy_end
    existing_session.flow_achieved = data.flow_achieved
    if data.notes:
        existing_session.notes = data.notes
    if data.blockers:
        existing_session.blockers = data.blockers

    existing_session.ended_at = datetime.utcnow()
    existing_session.status = "closed"

    # Calculate duration
    delta = existing_session.ended_at - existing_session.started_at
    existing_session.duration_minutes = int(delta.total_seconds() / 60)

    db.add(existing_session)
    db.commit()
    db.refresh(existing_session)
    return existing_session


def delete_session(session_id: UUID, user_id: UUID, db: SQLSession) -> None:
    session_to_delete = get_session(session_id, user_id, db)
    db.delete(session_to_delete)
    db.commit()
