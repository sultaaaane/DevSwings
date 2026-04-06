from celery.schedules import crontab
from app.workers.celery import celery_app

celery_app.conf.beat_schedule = {
    # Every night at 00:00 UTC
    "create-daily-digests-midnight": {
        "task": "create_daily_digests",
        "schedule": crontab(hour=0, minute=0),
    },
    # Every 4 hours to re-calculate long-term insights
    "recompute-insights-every-4-hours": {
        "task": "generate_all_insights",
        "schedule": crontab(minute=0, hour="*/4"),
    },
}
