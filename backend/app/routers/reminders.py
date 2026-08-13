from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import verify_reminder_open_token
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.schemas.reminder import ReminderListItem, ReminderListResponse, ReminderOpenedResponse, SnoozeResponse
from app.services.priority_engine import ensure_utc
from app.services.reminder_service import snooze_reminder

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])

_ALLOWED_SNOOZE_MINUTES = {15, 30, 60, 120}


def _format_time_until(trigger_time: datetime) -> str:
    delta = ensure_utc(trigger_time) - datetime.now(timezone.utc)
    if delta.total_seconds() <= 0:
        return "due now"
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes = remainder // 60
    return f"{hours} hours {minutes} minutes" if hours else f"{minutes} minutes"


@router.get("", response_model=ReminderListResponse)
def list_reminders(
    status_filter: Literal["pending", "delivered", "cancelled", "failed"] = Query("pending", alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderListResponse:
    query = (
        db.query(Reminder, Task.title)
        .join(Task, Task.task_id == Reminder.task_id)
        .filter(Reminder.user_id == current_user.user_id, Reminder.status == status_filter)
        .order_by(Reminder.trigger_time.asc())
    )
    total_count = query.count()
    rows = query.offset(offset).limit(limit).all()

    reminders = [
        ReminderListItem(
            reminder_id=reminder.reminder_id,
            task_id=reminder.task_id,
            task_title=title,
            trigger_time=reminder.trigger_time,
            status=reminder.status,
            delivered_at=reminder.delivered_at,
            opened_at=reminder.opened_at,
            time_until_delivery=_format_time_until(reminder.trigger_time) if reminder.status == "pending" else None,
        )
        for reminder, title in rows
    ]
    return ReminderListResponse(reminders=reminders, total_count=total_count)


@router.put("/{reminder_id}/opened", response_model=ReminderOpenedResponse)
def mark_opened(
    reminder_id: int,
    token: str = Query(..., description="HMAC from the push notification payload, proves this client received it"),
    db: Session = Depends(get_db),
) -> ReminderOpenedResponse:
    """Called by the service worker's notificationclick handler, which can't carry the
    user's JWT (no localStorage access from that context) -- see
    sign_reminder_open_token for why a per-reminder token is used instead of full auth.
    """
    if not verify_reminder_open_token(reminder_id, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    reminder = db.get(Reminder, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    if reminder.opened_at is None:
        reminder.opened_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reminder)

    return ReminderOpenedResponse(reminder_id=reminder.reminder_id, opened_at=reminder.opened_at)


@router.get("/{reminder_id}/snooze", response_model=SnoozeResponse)
def snooze(
    reminder_id: int,
    minutes: int = Query(..., description="15, 30, 60, or 120"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SnoozeResponse:
    if minutes not in _ALLOWED_SNOOZE_MINUTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"minutes must be one of {sorted(_ALLOWED_SNOOZE_MINUTES)}",
        )

    reminder = db.get(Reminder, reminder_id)
    if reminder is None or reminder.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    reminder = snooze_reminder(db, reminder, minutes)
    db.commit()
    db.refresh(reminder)

    return SnoozeResponse(
        reminder_id=reminder.reminder_id,
        status=reminder.status,
        new_trigger_time=reminder.trigger_time,
        message=f"Reminder postponed by {minutes} minutes",
    )
