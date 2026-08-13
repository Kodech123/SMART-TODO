from datetime import datetime, time, timedelta, timezone

from app.services.reminder_service import calculate_optimal_reminder_time

ACTIVE_START = time(8, 0)
ACTIVE_END = time(22, 0)
EARLY_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_reminder_fires_default_offset_minutes_before_due_time():
    due_date = datetime(2026, 1, 20, 14, 0, tzinfo=timezone.utc)  # within active hours already
    result = calculate_optimal_reminder_time(due_date, 30, ACTIVE_START, ACTIVE_END, now=EARLY_NOW)
    assert result == datetime(2026, 1, 20, 13, 30, tzinfo=timezone.utc)


def test_reminder_before_active_hours_clamps_to_start():
    due_date = datetime(2026, 1, 20, 8, 15, tzinfo=timezone.utc)  # 30 min before -> 07:45, before active_start
    result = calculate_optimal_reminder_time(due_date, 30, ACTIVE_START, ACTIVE_END, now=EARLY_NOW)
    assert result == datetime(2026, 1, 20, 8, 0, tzinfo=timezone.utc)


def test_reminder_after_active_hours_clamps_to_same_day():
    due_date = datetime(2026, 1, 20, 23, 30, tzinfo=timezone.utc)  # 90 min before -> 22:00, at active_end
    result = calculate_optimal_reminder_time(due_date, 90, ACTIVE_START, ACTIVE_END, now=EARLY_NOW)
    # Clamp to just before closing time on the *same* calendar day, not pushed back a day.
    assert result == datetime(2026, 1, 20, 21, 0, tzinfo=timezone.utc)


def test_near_term_due_date_does_not_schedule_a_reminder_in_the_past():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    due_date = now + timedelta(minutes=10)  # 30-minute offset would land before `now`
    result = calculate_optimal_reminder_time(due_date, 30, ACTIVE_START, ACTIVE_END, now=now)
    assert result > now
