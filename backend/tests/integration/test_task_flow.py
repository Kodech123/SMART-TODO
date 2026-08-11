def test_create_task_computes_priority_and_schedules_reminder(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Submit assignment for algorithms",
            "description": "Complete assignment on sorting algorithms",
            "category": "Academic",
            "due_date": "in 7 days",
            "importance_level": 4,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()

    assert body["priority_label"] in {"P1", "P2", "P3", "P4"}
    assert 0.0 <= body["priority_score"] <= 10.0
    assert body["scores"]["breakdown"]["final_calculation"]

    assert body["reminder"] is not None
    assert body["reminder"]["status"] == "pending"


def test_create_task_without_reminder_has_no_reminder(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Quick task with no reminder",
            "due_date": "in 2 days",
            "importance_level": 2,
            "estimated_effort": 2,
            "enable_reminder": False,
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["reminder"] is None


def test_update_due_date_recalculates_priority_and_reschedules_reminder(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task to reschedule",
            "due_date": "in 20 days",
            "importance_level": 2,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    )
    task_id = create.json()["task_id"]
    original_score = create.json()["priority_score"]
    original_reminder_id = create.json()["reminder"]["reminder_id"]

    update = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"due_date": "in 1 day", "importance_level": 5},
    )
    assert update.status_code == 200, update.text
    body = update.json()

    # Much closer due date + higher importance should raise the score.
    assert body["priority_score"] > original_score
    assert body["reminder"] is not None
    assert body["reminder"]["reminder_id"] != original_reminder_id

    reminders = client.get("/api/v1/reminders?status=cancelled", headers=auth_headers).json()
    assert any(r["reminder_id"] == original_reminder_id for r in reminders["reminders"])


def test_complete_task_cancels_reminder(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task to complete",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    )
    task_id = create.json()["task_id"]

    complete = client.put(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
    assert complete.status_code == 200, complete.text
    body = complete.json()
    assert body["status"] == "completed"
    assert body["reminder"]["status"] == "cancelled"

    detail = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers).json()
    assert detail["status"] == "completed"


def test_delete_task_removes_it(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task to delete",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": False,
        },
    )
    task_id = create.json()["task_id"]

    delete = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete.status_code == 204

    get_after_delete = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_after_delete.status_code == 404


def test_snooze_reminder_updates_trigger_time(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task with reminder to snooze",
            "due_date": "in 10 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    )
    reminder_id = create.json()["reminder"]["reminder_id"]
    original_trigger_time = create.json()["reminder"]["trigger_time"]

    snooze = client.get(f"/api/v1/reminders/{reminder_id}/snooze?minutes=30", headers=auth_headers)
    assert snooze.status_code == 200, snooze.text
    body = snooze.json()
    assert body["status"] == "pending"
    assert body["new_trigger_time"] != original_trigger_time


def test_task_list_sorted_by_priority_score_descending(client, auth_headers):
    low = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Low priority", "due_date": "in 60 days", "importance_level": 1, "estimated_effort": 5},
    ).json()
    high = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "High priority", "due_date": "in 1 day", "importance_level": 5, "estimated_effort": 1},
    ).json()

    listing = client.get("/api/v1/tasks", headers=auth_headers).json()
    ids_in_order = [t["task_id"] for t in listing["tasks"]]
    assert ids_in_order.index(high["task_id"]) < ids_in_order.index(low["task_id"])
