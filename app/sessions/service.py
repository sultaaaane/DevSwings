from uuid import UUID
from datetime import datetime
from sqlmodel import Session as DatabaseSession, select
from app.sessions.model import Session as SessionModel
from app.sessions.schemas import SessionCreate, SessionUpdate, SessionEnd
from app.streaks import service as streak_service


def create_session(
    data: SessionCreate, user_id: UUID, db: DatabaseSession
) -> SessionModel:
    session = SessionModel(**data.model_dump(), user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Update streak when a new session starts
    streak_service.update_user_streak(
        user_id, db, activity_date=session.started_at.date()
    )

    return session


def get_sessions(user_id: UUID, db: DatabaseSession) -> list[SessionModel]:
    return db.exec(select(SessionModel).where(SessionModel.user_id == user_id)).all()


def get_session(session_id: UUID, user_id: UUID, db: DatabaseSession) -> SessionModel:
    session = db.get(SessionModel, session_id)
    if not session or session.user_id != user_id:
        raise ValueError("Session not found")
    return session


def update_session(
    session_id: UUID, data: SessionUpdate, user_id: UUID, db: DatabaseSession
) -> SessionModel:
    session = get_session(session_id, user_id, db)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(session, field, value)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def end_session(
    session_id: UUID, data: SessionEnd, user_id: UUID, db: DatabaseSession
) -> SessionModel:
    session = get_session(session_id, user_id, db)
    if session.status == "closed":
        raise ValueError("Session already closed")

    session.energy_end = data.energy_end
    session.flow_achieved = data.flow_achieved
    if data.notes:
        session.notes = data.notes
    if data.blockers:
        session.blockers = data.blockers

    session.ended_at = datetime.utcnow()
    session.status = "closed"

    # Calculate duration
    delta = session.ended_at - session.started_at
    session.duration_minutes = int(delta.total_seconds() / 60)

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(session_id: UUID, user_id: UUID, db: DatabaseSession) -> None:
    session = get_session(session_id, user_id, db)
    db.delete(session)
    db.commit()
