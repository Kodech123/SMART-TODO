from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.category import Category
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.schemas.reminder import ReminderInfo
from app.schemas.task import (
    DailyCompletionCount,
    ScoreBreakdown,
    TaskCompleteResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskListItem,
    TaskListResponse,
    TaskStatsResponse,
    TaskUpdate,
)
from app.services import task_service
from app.services.priority_engine import PriorityBreakdown, days_remaining_until, explain_breakdown

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def _get_owned_task(db: Session, task_id: int, user_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _active_reminder(db: Session, task_id: int) -> Reminder | None:
    return (
        db.query(Reminder)
        .filter(Reminder.task_id == task_id, Reminder.status == "pending")
        .order_by(Reminder.trigger_time.desc())
        .first()
    )


def _reminder_info(reminder: Reminder | None) -> ReminderInfo | None:
    if reminder is None:
        return None
    return ReminderInfo(
        reminder_id=reminder.reminder_id,
        trigger_time=reminder.trigger_time,
        status=reminder.status,
        message=f"Reminder scheduled for {reminder.trigger_time.strftime('%Y-%m-%d %H:%M')}",
    )


def _to_list_item(task: Task) -> TaskListItem:
    return TaskListItem(
        task_id=task.task_id,
        title=task.title,
        category=task.category.category_name if task.category else None,
        due_date=task.due_date,
        priority_score=task.priority_score,
        priority_label=task.priority_label,
        status=task.status,
        days_remaining=days_remaining_until(task.due_date),
    )


def _to_detail_response(db: Session, task: Task) -> TaskDetailResponse:
    breakdown = PriorityBreakdown(
        urgency_score=task.urgency_score,
        importance_score=task.importance_score,
        deadline_proximity_score=task.deadline_proximity_score,
        effort_score=task.effort_score,
        priority_score=task.priority_score,
        priority_label=task.priority_label,
        days_remaining=days_remaining_until(task.due_date),
    )
    scores = ScoreBreakdown(
        urgency_score=task.urgency_score,
        importance_score=task.importance_score,
        deadline_proximity_score=task.deadline_proximity_score,
        effort_score=task.effort_score,
        breakdown=explain_breakdown(breakdown, task.importance_level, task.estimated_effort),
    )
    return TaskDetailResponse(
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        category=task.category.category_name if task.category else None,
        due_date=task.due_date,
        importance_level=task.importance_level,
        estimated_effort=task.estimated_effort,
        priority_score=task.priority_score,
        priority_label=task.priority_label,
        status=task.status,
        created_at=task.created_at,
        completed_at=task.completed_at,
        scores=scores,
        reminder=_reminder_info(_active_reminder(db, task.task_id)),
    )


@router.post("", response_model=TaskDetailResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> TaskDetailResponse:
    try:
        task = task_service.create_task(db, current_user, payload)
    except task_service.TaskValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors) from exc
    return _to_detail_response(db, task)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status_filter: Literal["active", "completed", "all"] = Query("active", alias="status"),
    category: str | None = Query(None),
    sort_by: Literal["priority_score", "due_date", "created_at"] = Query("priority_score"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    query = db.query(Task).filter(Task.user_id == current_user.user_id)

    if status_filter != "all":
        query = query.filter(Task.status == status_filter)
    if category:
        query = query.join(Task.category).filter(Category.category_name.ilike(category))

    total_count = query.count()

    sort_column = {
        "priority_score": Task.priority_score.desc(),
        "due_date": Task.due_date.asc(),
        "created_at": Task.created_at.desc(),
    }[sort_by]

    tasks = query.order_by(sort_column).offset(offset).limit(limit).all()

    return TaskListResponse(
        tasks=[_to_list_item(task) for task in tasks],
        total_count=total_count,
        page=(offset // limit) + 1,
        per_page=limit,
    )


@router.get("/stats", response_model=TaskStatsResponse)
def get_task_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TaskStatsResponse:
    tasks = db.query(Task).filter(Task.user_id == current_user.user_id, Task.status != "deleted").all()

    total = len(tasks)
    active = [t for t in tasks if t.status == "active"]
    completed = [t for t in tasks if t.status == "completed"]
    overdue = [t for t in active if days_remaining_until(t.due_date) < 0]

    distribution = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    for task in active:
        distribution[task.priority_label] += 1

    today = datetime.now(timezone.utc).date()
    last_7_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    completions_by_date = {day: 0 for day in last_7_days}
    for task in completed:
        completed_date = task.completed_at.date()
        if completed_date in completions_by_date:
            completions_by_date[completed_date] += 1

    return TaskStatsResponse(
        total_tasks=total,
        active_tasks=len(active),
        completed_tasks=len(completed),
        overdue_tasks=len(overdue),
        completion_rate=round(len(completed) / total, 4) if total else 0.0,
        priority_distribution=distribution,
        daily_completions=[
            DailyCompletionCount(date=day.isoformat(), count=count) for day, count in completions_by_date.items()
        ],
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> TaskDetailResponse:
    task = _get_owned_task(db, task_id, current_user.user_id)
    return _to_detail_response(db, task)


@router.patch("/{task_id}", response_model=TaskDetailResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskDetailResponse:
    task = _get_owned_task(db, task_id, current_user.user_id)
    try:
        task = task_service.update_task(db, current_user, task, payload)
    except task_service.TaskValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors) from exc
    return _to_detail_response(db, task)


@router.put("/{task_id}/complete", response_model=TaskCompleteResponse)
def complete_task(
    task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> TaskCompleteResponse:
    task = _get_owned_task(db, task_id, current_user.user_id)
    task = task_service.complete_task(db, task)

    latest_reminder = (
        db.query(Reminder)
        .filter(Reminder.task_id == task.task_id)
        .order_by(Reminder.reminder_id.desc())
        .first()
    )
    return TaskCompleteResponse(
        task_id=task.task_id,
        status=task.status,
        completed_at=task.completed_at,
        reminder=_reminder_info(latest_reminder),
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    task = _get_owned_task(db, task_id, current_user.user_id)
    task_service.delete_task(db, task)
