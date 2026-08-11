from datetime import datetime, timedelta, timezone

import dateparser

FALLBACK_OFFSET_DAYS = 7


def extract_due_date(raw_text: str, *, now: datetime | None = None) -> tuple[datetime, bool]:
    """Parse a due-date string (ISO 8601 or natural language like 'next Friday',
    'in 3 days', 'end of week'). Returns (due_date, was_fallback_used).

    Falls back to now + 7 days when the text can't be parsed at all, per spec.
    """
    now = now or datetime.now(timezone.utc)

    parsed = dateparser.parse(
        raw_text,
        settings={
            "RELATIVE_BASE": now,
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": True,
        },
    )

    if parsed is None:
        return now + timedelta(days=FALLBACK_OFFSET_DAYS), True

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed, False
