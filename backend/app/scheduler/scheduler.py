from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.db.session import engine as db_engine
from app.scheduler.jobs import rescore_active_tasks

_scheduler: BackgroundScheduler | None = None

RESCORE_JOB_ID = "rescore-active-tasks"
RESCORE_INTERVAL_MINUTES = 30


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
        # Reuses the app's own engine/pool (rather than a second one built from the URL)
        # so there's a single, consistently-configured connection pool to the database.
        _scheduler.add_jobstore(
            SQLAlchemyJobStore(engine=db_engine, tablename="apscheduler_jobs"),
            alias="default",
        )
    return _scheduler


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()

    scheduler.add_job(
        func=rescore_active_tasks,
        trigger=IntervalTrigger(minutes=RESCORE_INTERVAL_MINUTES),
        id=RESCORE_JOB_ID,
        replace_existing=True,
        misfire_grace_time=300,
    )


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
    # Reset the singleton (rather than leaving a stopped scheduler around) so the next
    # get_scheduler() call builds a fresh instance -- avoids relying on APScheduler's
    # shutdown-then-restart support, which is unreliable across versions. Matters most
    # for tests, where the FastAPI lifespan start/stops per TestClient context.
    _scheduler = None
