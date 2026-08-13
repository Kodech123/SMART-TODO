from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.services.notification import get_notification_transport
from app.services.notification.base import NotificationPayload
from app.services.priority_engine import calculate_priority


def deliver_reminder(reminder_id: int) -> None:
    """APScheduler job target. Runs on a background thread outside request scope,
    so it opens its own DB session rather than depending on the FastAPI `get_db` generator.
    Only a plain int (reminder_id) is ever passed as a job arg -- never a live ORM object,
    since APScheduler pickles job args into the persistent jobstore.
    """
    db = SessionLocal()
    try:
        reminder = db.get(Reminder, reminder_id)
        if reminder is None or reminder.status != "pending":
            return

        task = db.get(Task, reminder.task_id)
        if task is None or task.status != "active":
            reminder.status = "cancelled"
            db.commit()
            return

        user = db.get(User, reminder.user_id)
        if user is None or not user.notification_opt_in:
            reminder.status = "cancelled"
            db.commit()
            return

        transport = get_notification_transport()
        payload = NotificationPayload(
            title=f"Task Reminder: {task.title}",
            body=f"Priority: {task.priority_label} | Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}",
            task_id=task.task_id,
            reminder_id=reminder.reminder_id,
        )

        subscriptions = user.push_subscriptions
        if not subscriptions:
            # No registered push endpoint yet; the log transport still records the attempt
            # so the reminder pipeline is observable end-to-end in dev. WebPushTransport
            # must handle this {"endpoint": None} case gracefully itself (not crash) --
            # see its own guard for why.
            result = transport.send({"endpoint": None}, payload)
        else:
            results = [
                transport.send(
                    {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key}}, payload
                )
                for sub in subscriptions
            ]
            result = next((r for r in results if r.success), results[0])

        reminder.status = "delivered" if result.success else "failed"
        if result.success:
            reminder.delivered_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


def rescore_active_tasks() -> None:
    """Periodic job: urgency/deadline-proximity scores drift with time even without
    user edits, so active tasks are re-scored on an interval as deadlines approach.
    """
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.status == "active").all()
        for task in tasks:
            breakdown = calculate_priority(task.importance_level, task.estimated_effort, task.due_date)
            task.urgency_score = breakdown.urgency_score
            task.importance_score = breakdown.importance_score
            task.deadline_proximity_score = breakdown.deadline_proximity_score
            task.effort_score = breakdown.effort_score
            task.priority_score = breakdown.priority_score
            task.priority_label = breakdown.priority_label
            task.last_score_update = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()
