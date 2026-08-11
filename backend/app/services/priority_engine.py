from dataclasses import dataclass
from datetime import datetime, timezone

WEIGHTS = {
    "urgency": 0.35,
    "importance": 0.35,
    "deadline_proximity": 0.20,
    "effort": 0.10,
}


def ensure_utc(dt: datetime) -> datetime:
    """SQLite doesn't preserve tzinfo on round-trip; every datetime this app writes
    is UTC, so a naive value read back can be safely assumed UTC rather than
    compared naively.
    """
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class PriorityBreakdown:
    urgency_score: float
    importance_score: float
    deadline_proximity_score: float
    effort_score: float
    priority_score: float
    priority_label: str
    days_remaining: int


def calculate_priority(
    importance_level: int,
    estimated_effort: int,
    due_date: datetime,
    now: datetime | None = None,
) -> PriorityBreakdown:
    """Weighted-formula priority score (Eisenhower-style: urgency + importance as
    primary factors, deadline proximity secondary, effort as a tiebreaker).

    `days_remaining` is computed unclamped so overdue tasks (negative value) can be
    detected; it is then floored at 0 before feeding the urgency/deadline-proximity
    formulas, per the algorithm spec.
    """
    now = ensure_utc(now or datetime.now(timezone.utc))
    due_date = ensure_utc(due_date)
    raw_days_remaining = (due_date - now).days
    is_overdue = raw_days_remaining < 0
    days_remaining = 0 if is_overdue else raw_days_remaining

    urgency_score = 10.0 if is_overdue else max(0.0, 10.0 - (days_remaining / 3.0))
    importance_score = importance_level * 2.0
    deadline_proximity_score = max(0.0, 10.0 - (days_remaining / 5.0))
    effort_score = (6.0 - estimated_effort) * 2.0

    priority_score = (
        WEIGHTS["urgency"] * urgency_score
        + WEIGHTS["importance"] * importance_score
        + WEIGHTS["deadline_proximity"] * deadline_proximity_score
        + WEIGHTS["effort"] * effort_score
    )
    priority_score = min(10.0, max(0.0, priority_score))

    return PriorityBreakdown(
        urgency_score=round(urgency_score, 4),
        importance_score=round(importance_score, 4),
        deadline_proximity_score=round(deadline_proximity_score, 4),
        effort_score=round(effort_score, 4),
        priority_score=round(priority_score, 4),
        priority_label=label_for_score(priority_score),
        days_remaining=raw_days_remaining,
    )


def days_remaining_until(due_date: datetime, now: datetime | None = None) -> int:
    now = ensure_utc(now or datetime.now(timezone.utc))
    return (ensure_utc(due_date) - now).days


def label_for_score(score: float) -> str:
    if score >= 8.0:
        return "P1"
    if score >= 6.0:
        return "P2"
    if score >= 4.0:
        return "P3"
    return "P4"


def explain_breakdown(breakdown: PriorityBreakdown, importance_level: int, estimated_effort: int) -> dict[str, str]:
    days = max(0, breakdown.days_remaining)
    return {
        "urgency_calculation": (
            "10.0 (overdue)"
            if breakdown.days_remaining < 0
            else f"max(0, 10 - ({days} days / 3)) = {breakdown.urgency_score}"
        ),
        "importance_calculation": f"{importance_level} × 2 = {breakdown.importance_score}",
        "deadline_proximity_calculation": f"max(0, 10 - ({days} / 5)) = {breakdown.deadline_proximity_score}",
        "effort_calculation": f"(6 - {estimated_effort}) × 2 = {breakdown.effort_score}",
        "final_calculation": (
            f"{WEIGHTS['urgency']}×{breakdown.urgency_score} + {WEIGHTS['importance']}×{breakdown.importance_score} "
            f"+ {WEIGHTS['deadline_proximity']}×{breakdown.deadline_proximity_score} "
            f"+ {WEIGHTS['effort']}×{breakdown.effort_score} = {breakdown.priority_score}"
        ),
    }
