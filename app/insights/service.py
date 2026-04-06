from uuid import UUID
from sqlmodel import Session, select, func
from app.insights.model import Insight
from app.sessions.model import WorkSession as SessionModel
from app.commits.model import Commit
from app.insights.schemas import StatsSummary


def get_user_stats(
    user_id: UUID, db: Session, project_id: UUID | None = None
) -> StatsSummary:
    # --- GET SESSIONS STATS ---
    session_stmt = select(SessionModel).where(SessionModel.user_id == user_id)
    if project_id:
        session_stmt = session_stmt.where(SessionModel.project_id == project_id)

    sessions = db.exec(session_stmt).all()

    total_sessions = len(sessions)
    total_duration = sum((s.duration_minutes or 0) for s in sessions)

    # average energy start
    energy_starts = [s.energy_start for s in sessions]
    avg_energy_start = (
        sum(energy_starts) / total_sessions if total_sessions > 0 else None
    )

    # average energy end
    energy_ends = [s.energy_end for s in sessions if s.energy_end is not None]
    avg_energy_end = (
        sum(energy_ends) / len(energy_ends) if len(energy_ends) > 0 else None
    )

    # flow count
    flow_count = sum(1 for s in sessions if s.flow_achieved)

    # --- GET COMMITS STATS ---
    commit_stmt = select(func.count(Commit.id)).where(Commit.user_id == user_id)
    if project_id:
        commit_stmt = commit_stmt.where(Commit.project_id == project_id)

    total_commits = db.exec(commit_stmt).one()

    return StatsSummary(
        total_sessions=total_sessions,
        total_duration_minutes=total_duration,
        total_commits=total_commits,
        average_energy_start=avg_energy_start,
        average_energy_end=avg_energy_end,
        flow_sessions_count=flow_count,
    )


def list_insights(user_id: UUID, db: Session) -> list[Insight]:
    return db.exec(select(Insight).where(Insight.user_id == user_id)).all()
