from datetime import time

from pydantic import BaseModel, ConfigDict, EmailStr


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
    display_name: str
    active_hours_start: time
    active_hours_end: time
    default_reminder_minutes: int
    notification_opt_in: bool


class UserSettingsUpdate(BaseModel):
    display_name: str | None = None
    active_hours_start: time | None = None
    active_hours_end: time | None = None
    default_reminder_minutes: int | None = None
    notification_opt_in: bool | None = None
