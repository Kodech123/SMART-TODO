"""Task completion time and reminder effectiveness report, for the project's
evaluation methodology (task completion time, reminder effectiveness).

Reads whatever is in the configured database (DATABASE_URL) -- on a fresh dev
DB this reports "no data yet"; the numbers only mean something once real
usage (ideally the UAT period) has produced completed tasks and delivered
reminders.

Usage:
    cd backend
    python scripts/evaluation_report.py
"""

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal  # noqa: E402
from app.models.reminder import Reminder  # noqa: E402
from app.models.task import Task  # noqa: E402
from app.services.priority_engine import ensure_utc  # noqa: E402

REMINDER_EFFECTIVE_WINDOW_MINUTES = 30


def _fmt_duration(seconds: float) -> str:
    hours = seconds / 3600
    if hours >= 1:
        return f"{hours:.1f}h"
    return f"{seconds / 60:.1f}m"


def task_completion_report(db) -> None:
    print("\n=== Task completion time ===")
    completed = db.query(Task).filter(Task.status == "completed", Task.completed_at.isnot(None)).all()

    if not completed:
        print("No completed tasks yet -- nothing to report.")
        return

    by_label: dict[str, list[float]] = {}
    all_durations: list[float] = []
    for task in completed:
        duration = (ensure_utc(task.completed_at) - ensure_utc(task.created_at)).total_seconds()
        all_durations.append(duration)
        by_label.setdefault(task.priority_label, []).append(duration)

    print(f"n={len(completed)}  mean={_fmt_duration(statistics.mean(all_durations))}  "
          f"median={_fmt_duration(statistics.median(all_durations))}")
    for label in sorted(by_label):
        durations = by_label[label]
        print(f"  {label}: n={len(durations)}  mean={_fmt_duration(statistics.mean(durations))}  "
              f"median={_fmt_duration(statistics.median(durations))}")


def reminder_effectiveness_report(db) -> None:
    print("\n=== Reminder effectiveness ===")
    delivered = db.query(Reminder).filter(Reminder.delivered_at.isnot(None)).all()

    if not delivered:
        print("No delivered reminders yet -- nothing to report.")
        return

    opened = [r for r in delivered if r.opened_at is not None]
    open_rate = len(opened) / len(delivered) * 100

    print(f"delivered={len(delivered)}  opened={len(opened)}  open_rate={open_rate:.1f}%")

    if not opened:
        return

    minutes_to_open = [
        (ensure_utc(r.opened_at) - ensure_utc(r.delivered_at)).total_seconds() / 60 for r in opened
    ]
    within_window = sum(1 for m in minutes_to_open if m <= REMINDER_EFFECTIVE_WINDOW_MINUTES)
    effectiveness = within_window / len(opened) * 100

    print(f"opened within {REMINDER_EFFECTIVE_WINDOW_MINUTES}m: {within_window}/{len(opened)} "
          f"({effectiveness:.1f}%)")
    print(f"mean time-to-open={statistics.mean(minutes_to_open):.1f}m  "
          f"median={statistics.median(minutes_to_open):.1f}m")


def main() -> None:
    db = SessionLocal()
    try:
        task_completion_report(db)
        reminder_effectiveness_report(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
