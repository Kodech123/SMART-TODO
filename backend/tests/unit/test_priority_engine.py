from datetime import datetime, timedelta, timezone

import pytest

from app.services.priority_engine import calculate_priority, label_for_score

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_overdue_task_gets_max_urgency():
    """Overdue tasks must score urgency_score == 10.0, regardless of importance/effort."""
    breakdown = calculate_priority(
        importance_level=3, estimated_effort=2, due_date=NOW - timedelta(days=1), now=NOW
    )
    assert breakdown.urgency_score == 10.0
    assert breakdown.days_remaining < 0


def test_priority_formula_matches_hand_calculation():
    """due in exactly 10 days, importance=3, effort=5 -- hand-verified against the
    weighted formula (urgency 0.35 / importance 0.35 / deadline-proximity 0.20 / effort 0.10).
    """
    breakdown = calculate_priority(
        importance_level=3, estimated_effort=5, due_date=NOW + timedelta(days=10), now=NOW
    )
    assert breakdown.urgency_score == pytest.approx(6.6667, abs=1e-3)
    assert breakdown.importance_score == 6.0
    assert breakdown.deadline_proximity_score == 8.0
    assert breakdown.effort_score == 2.0
    assert breakdown.priority_score == pytest.approx(6.2333, abs=1e-3)
    assert breakdown.priority_label == "P2"


def test_due_today_maximizes_time_based_scores():
    breakdown = calculate_priority(importance_level=3, estimated_effort=3, due_date=NOW, now=NOW)
    assert breakdown.urgency_score == 10.0
    assert breakdown.deadline_proximity_score == 10.0


def test_far_future_due_date_zeroes_time_based_scores():
    breakdown = calculate_priority(
        importance_level=1, estimated_effort=1, due_date=NOW + timedelta(days=365), now=NOW
    )
    assert breakdown.urgency_score == 0.0
    assert breakdown.deadline_proximity_score == 0.0


@pytest.mark.parametrize(
    "importance_level,expected_importance_score",
    [(1, 2.0), (2, 4.0), (3, 6.0), (4, 8.0), (5, 10.0)],
)
def test_importance_score_scales_linearly(importance_level, expected_importance_score):
    breakdown = calculate_priority(
        importance_level=importance_level, estimated_effort=3, due_date=NOW + timedelta(days=5), now=NOW
    )
    assert breakdown.importance_score == expected_importance_score


@pytest.mark.parametrize(
    "estimated_effort,expected_effort_score",
    [(1, 10.0), (2, 8.0), (3, 6.0), (4, 4.0), (5, 2.0)],
)
def test_effort_score_is_inverted(estimated_effort, expected_effort_score):
    """Lower effort should score higher (momentum-building principle)."""
    breakdown = calculate_priority(
        importance_level=3, estimated_effort=estimated_effort, due_date=NOW + timedelta(days=5), now=NOW
    )
    assert breakdown.effort_score == expected_effort_score


@pytest.mark.parametrize(
    "score,expected_label",
    [(10.0, "P1"), (8.0, "P1"), (7.999, "P2"), (6.0, "P2"), (5.999, "P3"), (4.0, "P3"), (3.999, "P4"), (0.0, "P4")],
)
def test_priority_label_boundaries(score, expected_label):
    assert label_for_score(score) == expected_label


def test_priority_score_is_always_within_bounds():
    for importance in range(1, 6):
        for effort in range(1, 6):
            for days in (-5, 0, 1, 3, 7, 30, 400):
                breakdown = calculate_priority(
                    importance_level=importance,
                    estimated_effort=effort,
                    due_date=NOW + timedelta(days=days),
                    now=NOW,
                )
                assert 0.0 <= breakdown.priority_score <= 10.0
