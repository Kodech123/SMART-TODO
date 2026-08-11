from datetime import datetime, timedelta, timezone

from app.services.date_parser import FALLBACK_OFFSET_DAYS, extract_due_date

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def test_parses_iso_datetime():
    due_date, used_fallback = extract_due_date("2026-12-25T17:00:00Z", now=NOW)
    assert due_date.year == 2026
    assert due_date.month == 12
    assert due_date.day == 25
    assert used_fallback is False


def test_parses_relative_phrase_in_3_days():
    due_date, used_fallback = extract_due_date("in 3 days", now=NOW)
    assert due_date.date() == (NOW + timedelta(days=3)).date()
    assert used_fallback is False


def test_parses_tomorrow():
    due_date, used_fallback = extract_due_date("tomorrow at 5pm", now=NOW)
    assert due_date.date() == (NOW + timedelta(days=1)).date()
    assert due_date.hour == 17
    assert used_fallback is False


def test_unparseable_text_falls_back_to_seven_days():
    due_date, used_fallback = extract_due_date("asdkjhaslkdjh not a date at all !!!", now=NOW)
    assert used_fallback is True
    assert due_date.date() == (NOW + timedelta(days=FALLBACK_OFFSET_DAYS)).date()


def test_returned_datetime_is_always_timezone_aware():
    due_date, _ = extract_due_date("next Friday", now=NOW)
    assert due_date.tzinfo is not None
