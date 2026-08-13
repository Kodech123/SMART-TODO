from app.core.security import sign_reminder_open_token
from app.scheduler.jobs import deliver_reminder, rescore_active_tasks


def test_list_pending_reminders_includes_time_until_delivery(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task with a pending reminder",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    reminder_id = task["reminder"]["reminder_id"]

    # Default status filter is "pending" -- the only status that formats time_until_delivery,
    # which requires comparing the DB-round-tripped trigger_time against datetime.now().
    response = client.get("/api/v1/reminders", headers=auth_headers)

    assert response.status_code == 200
    entry = next(r for r in response.json()["reminders"] if r["reminder_id"] == reminder_id)
    assert entry["time_until_delivery"] is not None


def test_deliver_reminder_marks_pending_reminder_delivered(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task with reminder",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    reminder_id = task["reminder"]["reminder_id"]

    deliver_reminder(reminder_id)

    delivered = client.get("/api/v1/reminders?status=delivered", headers=auth_headers).json()
    assert any(r["reminder_id"] == reminder_id for r in delivered["reminders"])


def test_deliver_reminder_is_a_noop_for_already_cancelled_reminder(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task that gets completed first",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    reminder_id = task["reminder"]["reminder_id"]
    client.put(f"/api/v1/tasks/{task['task_id']}/complete", headers=auth_headers)

    deliver_reminder(reminder_id)  # should not raise, and must not resurrect the cancelled reminder

    cancelled = client.get("/api/v1/reminders?status=cancelled", headers=auth_headers).json()
    assert any(r["reminder_id"] == reminder_id for r in cancelled["reminders"])
    delivered = client.get("/api/v1/reminders?status=delivered", headers=auth_headers).json()
    assert not any(r["reminder_id"] == reminder_id for r in delivered["reminders"])


def test_mark_opened_records_timestamp_with_valid_token(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task with reminder to open",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    reminder_id = task["reminder"]["reminder_id"]
    token = sign_reminder_open_token(reminder_id)

    response = client.put(f"/api/v1/reminders/{reminder_id}/opened?token={token}")

    assert response.status_code == 200, response.text
    assert response.json()["opened_at"] is not None

    listed = client.get("/api/v1/reminders", headers=auth_headers).json()
    entry = next(r for r in listed["reminders"] if r["reminder_id"] == reminder_id)
    assert entry["opened_at"] is not None


def test_mark_opened_is_idempotent(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task opened twice",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    reminder_id = task["reminder"]["reminder_id"]
    token = sign_reminder_open_token(reminder_id)

    first = client.put(f"/api/v1/reminders/{reminder_id}/opened?token={token}").json()
    second = client.put(f"/api/v1/reminders/{reminder_id}/opened?token={token}").json()

    assert first["opened_at"] == second["opened_at"]


def test_mark_opened_rejects_invalid_token(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task with forged token attempt",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    reminder_id = task["reminder"]["reminder_id"]

    response = client.put(f"/api/v1/reminders/{reminder_id}/opened?token=not-the-real-token")

    assert response.status_code == 403


def test_rescore_active_tasks_recomputes_scores_without_error(client, auth_headers):
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task to rescore",
            "due_date": "in 15 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": False,
        },
    ).json()
    before = client.get(f"/api/v1/tasks/{task['task_id']}", headers=auth_headers).json()

    rescore_active_tasks()

    after = client.get(f"/api/v1/tasks/{task['task_id']}", headers=auth_headers).json()
    # Due date is unchanged and negligible time has passed, so the score should be stable.
    assert after["priority_score"] == before["priority_score"]
