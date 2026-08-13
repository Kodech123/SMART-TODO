import logging
from datetime import datetime, time, timedelta, timezone

from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.scheduler.jobs import deliver_reminder
from app.scheduler.scheduler import get_scheduler
from app.services.priority_engine import ensure_utc

logger = logging.getLogger("dosmart.reminders")


def calculate_optimal_reminder_time(
    due_date: datetime,
    default_reminder_minutes: int,
    active_hours_start: time,
    active_hours_end: time,
    *,
    now: datetime | None = None,
) -> datetime:
    """The user's configured offset before the deadline, clamped into their active hours.

    Priority (P1-P4) intentionally has no bearing on reminder timing -- it still drives
    sorting, badges, and urgency scoring elsewhere, but every task reminds the same
    fixed amount of time before its own due date, per the user's own setting.
    """
    due_date = ensure_utc(due_date)
    reminder_time = due_date - timedelta(minutes=default_reminder_minutes)

    active_start_hour, active_end_hour = active_hours_start.hour, active_hours_end.hour
    if reminder_time.hour < active_start_hour:
        reminder_time = reminder_time.replace(hour=active_start_hour, minute=0, second=0, microsecond=0)
    elif reminder_time.hour >= active_end_hour:
        # Clamp to just before closing time on the *same* calendar day. This datetime's
        # date is already correct (Python normalizes the hour after arithmetic), so an
        # extra day subtraction here would push the reminder a full day earlier than the
        # offset table intends -- e.g. P4's "5 days before" silently becoming 6+ days.
        reminder_time = reminder_time.replace(
            hour=max(active_end_hour - 1, active_start_hour), minute=0, second=0, microsecond=0
        )

    # A near-term due date can push the computed time into the past; rather than silently
    # dropping the reminder, fire it shortly so the user still gets notified.
    now = ensure_utc(now or datetime.now(timezone.utc))
    if reminder_time <= now:
        reminder_time = now + timedelta(minutes=1)

    return reminder_time


def _remove_job_if_exists(job_id: str) -> None:
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(job_id)
    except Exception:
        logger.debug("No scheduler job to remove for job_id=%s", job_id)


def create_pending_reminder(db: Session, task: Task, user: User) -> Reminder | None:
    """Create (and flush, to assign a PK) a pending Reminder row -- but do NOT register
    its APScheduler job yet. Requires `task.task_id` to already be set, and returns None
    if the user opted out of notifications.

    Job registration is a separate step (register_reminder_job) that callers must run
    *after* committing: APScheduler's jobstore writes through its own connection, and
    SQLite only allows one writer at a time. If this session still has an uncommitted
    write (e.g. from this same flush) when add_job() is called, the two writers
    deadlock on the same request/thread -- Postgres wouldn't have this problem, but the
    ordering is correct regardless of backend, so it's not backend-conditional.
    """
    if not user.notification_opt_in:
        return None

    trigger_time = calculate_optimal_reminder_time(
        task.due_date, user.default_reminder_minutes, user.active_hours_start, user.active_hours_end
    )

    reminder = Reminder(
        task_id=task.task_id,
        user_id=user.user_id,
        trigger_time=trigger_time,
        job_id=f"reminder-pending-{task.task_id}",
        status="pending",
    )
    db.add(reminder)
    db.flush()  # assign reminder.reminder_id
    reminder.job_id = f"reminder-{reminder.reminder_id}"
    return reminder


def register_reminder_job(reminder: Reminder) -> None:
    """Call only after the session holding `reminder` has been committed."""
    get_scheduler().add_job(
        func=deliver_reminder,
        trigger=DateTrigger(run_date=reminder.trigger_time),
        args=[reminder.reminder_id],
        id=reminder.job_id,
        replace_existing=True,
        misfire_grace_time=300,
    )


def cancel_reminders_for_task(db: Session, task: Task) -> None:
    pending = db.query(Reminder).filter(Reminder.task_id == task.task_id, Reminder.status == "pending").all()
    for reminder in pending:
        _remove_job_if_exists(reminder.job_id)
        reminder.status = "cancelled"


def reschedule_reminder_for_task(db: Session, task: Task, user: User) -> Reminder | None:
    """Cancels any pending reminder and creates a new pending row. Like
    create_pending_reminder, this does NOT register the new job -- call
    register_reminder_job() on the result after committing.
    """
    cancel_reminders_for_task(db, task)
    return create_pending_reminder(db, task, user)


def snooze_reminder(db: Session, reminder: Reminder, minutes: int) -> Reminder:
    new_trigger_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    get_scheduler().add_job(
        func=deliver_reminder,
        trigger=DateTrigger(run_date=new_trigger_time),
        args=[reminder.reminder_id],
        id=reminder.job_id,
        replace_existing=True,
        misfire_grace_time=300,
    )
    reminder.trigger_time = new_trigger_time
    reminder.status = "pending"
    return reminder
