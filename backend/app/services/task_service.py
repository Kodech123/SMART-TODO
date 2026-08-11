from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import reminder_service
from app.services.category_classifier import classify_category
from app.services.date_parser import extract_due_date
from app.services.priority_engine import calculate_priority


class TaskValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class TaskNotFoundError(Exception):
    pass


def _resolve_category(db: Session, user_id: int, category_name: str | None, title: str, description: str | None) -> Category | None:
    name = category_name or classify_category(title, description)

    category = (
        db.query(Category)
        .filter(Category.user_id == user_id, Category.category_name.ilike(name))
        .first()
    )
    if category is not None:
        return category

    # Unrecognized custom category name: fall back to the user's "Personal" default
    # rather than silently creating a new category from a typo'd task field.
    return db.query(Category).filter(Category.user_id == user_id, Category.category_name == "Personal").first()


def _apply_priority(task: Task) -> None:
    breakdown = calculate_priority(task.importance_level, task.estimated_effort, task.due_date)
    task.urgency_score = breakdown.urgency_score
    task.importance_score = breakdown.importance_score
    task.deadline_proximity_score = breakdown.deadline_proximity_score
    task.effort_score = breakdown.effort_score
    task.priority_score = breakdown.priority_score
    task.priority_label = breakdown.priority_label
    task.last_score_update = datetime.now(timezone.utc)


def create_task(db: Session, user: User, payload: TaskCreate) -> Task:
    due_date, _used_fallback = extract_due_date(payload.due_date)
    if due_date < datetime.now(timezone.utc):
        raise TaskValidationError(["Due date cannot be in the past"])

    category = _resolve_category(db, user.user_id, payload.category, payload.title, payload.description)

    task = Task(
        user_id=user.user_id,
        category_id=category.category_id if category else None,
        title=payload.title.strip(),
        description=(payload.description or "").strip() or None,
        importance_level=payload.importance_level,
        estimated_effort=payload.estimated_effort,
        due_date=due_date,
        status="active",
    )
    _apply_priority(task)

    db.add(task)
    db.flush()  # assign task.task_id before creating a reminder row against it

    reminder = None
    if payload.enable_reminder:
        reminder = reminder_service.create_pending_reminder(db, task, user)

    db.commit()
    db.refresh(task)

    # Registering the APScheduler job happens after commit -- see create_pending_reminder's
    # docstring for why (same-request writer/writer deadlock otherwise).
    if reminder is not None:
        reminder_service.register_reminder_job(reminder)

    return task


def update_task(db: Session, user: User, task: Task, payload: TaskUpdate) -> Task:
    fields = payload.model_dump(exclude_unset=True)

    rescheduling_relevant = False

    if "title" in fields:
        task.title = fields["title"].strip()
    if "description" in fields:
        task.description = (fields["description"] or "").strip() or None
    if "category" in fields:
        category = _resolve_category(db, user.user_id, fields["category"], task.title, task.description)
        task.category_id = category.category_id if category else None
    if "due_date" in fields:
        due_date, _used_fallback = extract_due_date(fields["due_date"])
        if due_date < datetime.now(timezone.utc):
            raise TaskValidationError(["Due date cannot be in the past"])
        task.due_date = due_date
        rescheduling_relevant = True
    if "importance_level" in fields:
        task.importance_level = fields["importance_level"]
        rescheduling_relevant = True
    if "estimated_effort" in fields:
        task.estimated_effort = fields["estimated_effort"]

    if rescheduling_relevant or "importance_level" in fields or "estimated_effort" in fields:
        _apply_priority(task)

    new_reminder = None
    if rescheduling_relevant and task.status == "active":
        new_reminder = reminder_service.reschedule_reminder_for_task(db, task, user)

    db.commit()
    db.refresh(task)

    if new_reminder is not None:
        reminder_service.register_reminder_job(new_reminder)

    return task


def complete_task(db: Session, task: Task) -> Task:
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    reminder_service.cancel_reminders_for_task(db, task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    reminder_service.cancel_reminders_for_task(db, task)
    db.delete(task)
    db.commit()
