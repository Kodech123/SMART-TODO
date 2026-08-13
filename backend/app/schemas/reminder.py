from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReminderInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reminder_id: int
    trigger_time: datetime
    status: str
    message: str | None = None


class ReminderListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reminder_id: int
    task_id: int
    task_title: str
    trigger_time: datetime
    status: str
    delivered_at: datetime | None = None
    opened_at: datetime | None = None
    time_until_delivery: str | None = None


class ReminderOpenedResponse(BaseModel):
    reminder_id: int
    opened_at: datetime


class ReminderListResponse(BaseModel):
    reminders: list[ReminderListItem]
    total_count: int


class SnoozeResponse(BaseModel):
    reminder_id: int
    status: str
    new_trigger_time: datetime
    message: str
