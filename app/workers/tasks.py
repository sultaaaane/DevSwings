from datetime import datetime, date, timedelta
from sqlmodel import Session, select
from app.workers.celery import celery_app
from app.core.database import engine
from app.users.model import User
from app.insights.model import Insight
from app.digests.model import Digest
from app.insights.service import get_user_stats


@celery_app.task(name="generate_all_insights")
def generate_all_insights():
    """Periodic task to generate insights for all active users."""
    with Session(engine) as db:
        users = db.exec(select(User).where(User.is_active == True)).all()
        for user in users:
            generate_user_insights.delay(str(user.id))


@celery_app.task(name="generate_user_insights")
def generate_user_insights(user_id_str: str):
    """Generates and persists insights for a specific user."""
    from uuid import UUID

    user_id = UUID(user_id_str)

    with Session(engine) as db:
        stats = get_user_stats(user_id, db)

        # Simple Example Insight: Flow rate
        flow_rate = (
            (stats.flow_sessions_count / stats.total_sessions * 100)
            if stats.total_sessions > 0
            else 0
        )

        new_insight = Insight(
            user_id=user_id,
            type="flow_efficiency",
            value={
                "flow_rate": flow_rate,
                "total_sessions": stats.total_sessions,
                "period": "lifetime",
            },
        )
        db.add(new_insight)
        db.commit()


@celery_app.task(name="create_daily_digests")
def create_daily_digests():
    """Periodic task to create daily digests for all active users."""
    yesterday = date.today() - timedelta(days=1)

    with Session(engine) as db:
        users = db.exec(select(User).where(User.is_active == True)).all()
        for user in users:
            # Create a simple digest record
            stats = get_user_stats(user.id, db)

            digest = Digest(
                user_id=user.id,
                period_start=yesterday,
                period_end=yesterday,
                content={
                    "sessions_completed": stats.total_sessions,
                    "total_minutes": stats.total_duration_minutes,
                    "commits_count": stats.total_commits,
                },
                delivered_at=datetime.utcnow(),
            )
            db.add(digest)
        db.commit()
