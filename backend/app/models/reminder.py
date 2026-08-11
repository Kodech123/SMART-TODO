from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'delivered', 'cancelled', 'failed')", name="ck_reminder_status_values"
        ),
        Index("idx_user_trigger", "user_id", "trigger_time"),
    )

    reminder_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped["Task"] = relationship(back_populates="reminders")
    user: Mapped["User"] = relationship(back_populates="reminders")
