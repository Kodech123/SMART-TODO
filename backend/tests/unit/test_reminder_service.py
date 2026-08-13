from datetime import datetime, time, timedelta, timezone

from app.services.reminder_service import calculate_optimal_reminder_time

ACTIVE_START = time(8, 0)
ACTIVE_END = time(22, 0)
EARLY_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_p1_offset_is_one_day_before_due_time():
    due_date = datetime(2026, 1, 20, 14, 0, tzinfo=timezone.utc)  # within active hours already
    result = calculate_optimal_reminder_time(due_date, "P1", ACTIVE_START, ACTIVE_END, now=EARLY_NOW)
    assert result == datetime(2026, 1, 19, 14, 0, tzinfo=timezone.utc)


def test_reminder_before_active_hours_clamps_to_start():
    due_date = datetime(2026, 1, 20, 10, 0, tzinfo=timezone.utc)  # P2 offset: 2 days, 9 hours -> 01:00
    result = calculate_optimal_reminder_time(due_date, "P2", ACTIVE_START, ACTIVE_END, now=EARLY_NOW)
    assert result == datetime(2026, 1, 18, 8, 0, tzinfo=timezone.utc)


def test_reminder_after_active_hours_clamps_to_same_day():
    due_date = datetime(2026, 1, 20, 23, 0, tzinfo=timezone.utc)  # P1 offset: 1 day, 0 hours -> Jan 19, 23:00
    result = calculate_optimal_reminder_time(due_date, "P1", ACTIVE_START, ACTIVE_END, now=EARLY_NOW)
    # 23:00 is past active_end (22:00), so clamp to just before closing -- on the *same*
    # calendar day (Jan 19, still "1 day before"), not pushed back an extra day to Jan 18.
    assert result == datetime(2026, 1, 19, 21, 0, tzinfo=timezone.utc)


def test_near_term_due_date_does_not_schedule_a_reminder_in_the_past():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    due_date = now + timedelta(hours=1)  # P1 offset of 1 day would land before `now`
    result = calculate_optimal_reminder_time(due_date, "P1", ACTIVE_START, ACTIVE_END, now=now)
    assert result > now
