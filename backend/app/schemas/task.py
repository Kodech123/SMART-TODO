from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.reminder import ReminderInfo


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    description: str | None = None
    category: str | None = None
    due_date: str = Field(description="ISO 8601 timestamp or natural language, e.g. 'next Friday'")
    importance_level: int = Field(ge=1, le=5)
    estimated_effort: int = Field(ge=1, le=5)
    enable_reminder: bool = True


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=500)
    description: str | None = None
    category: str | None = None
    due_date: str | None = None
    importance_level: int | None = Field(default=None, ge=1, le=5)
    estimated_effort: int | None = Field(default=None, ge=1, le=5)


class ScoreBreakdown(BaseModel):
    urgency_score: float
    importance_score: float
    deadline_proximity_score: float
    effort_score: float
    breakdown: dict[str, str] | None = None


class TaskListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    title: str
    category: str | None
    due_date: datetime
    priority_score: float
    priority_label: str
    status: str
    days_remaining: int


class TaskListResponse(BaseModel):
    tasks: list[TaskListItem]
    total_count: int
    page: int
    per_page: int


class TaskDetailResponse(BaseModel):
    task_id: int
    title: str
    description: str | None
    category: str | None
    due_date: datetime
    importance_level: int
    estimated_effort: int
    priority_score: float
    priority_label: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    scores: ScoreBreakdown
    reminder: ReminderInfo | None = None


class TaskCompleteResponse(BaseModel):
    task_id: int
    status: str
    completed_at: datetime
    reminder: ReminderInfo | None = None


class DailyCompletionCount(BaseModel):
    date: str
    count: int


class TaskStatsResponse(BaseModel):
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_rate: float
    priority_distribution: dict[str, int]
    daily_completions: list[DailyCompletionCount]
