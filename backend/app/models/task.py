from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("importance_level BETWEEN 1 AND 5", name="ck_importance_level_range"),
        CheckConstraint("estimated_effort BETWEEN 1 AND 5", name="ck_estimated_effort_range"),
        CheckConstraint("priority_label IN ('P1', 'P2', 'P3', 'P4')", name="ck_priority_label_values"),
        CheckConstraint("status IN ('active', 'completed', 'deleted')", name="ck_status_values"),
        Index("idx_user_status", "user_id", "status"),
        Index("idx_priority_score", "user_id", "priority_score"),
        Index("idx_due_date", "user_id", "due_date"),
    )

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    # Nullable + SET NULL (not the spec's literal NOT NULL) so deleting a category doesn't
    # cascade-delete or block on its tasks; the task just becomes "Uncategorized".
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance_level: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_effort: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    urgency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    deadline_proximity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    effort_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    priority_label: Mapped[str] = mapped_column(String(2), nullable=False, default="P4", server_default="P4")

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_score_update: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="tasks")
    category: Mapped["Category | None"] = relationship(back_populates="tasks")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="task", cascade="all, delete-orphan")
