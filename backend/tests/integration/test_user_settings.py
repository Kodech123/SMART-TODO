def test_get_settings_returns_defaults(client, auth_headers):
    response = client.get("/api/v1/user/settings", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["active_hours_start"] == "08:00:00"
    assert body["active_hours_end"] == "22:00:00"
    assert body["notification_opt_in"] is True


def test_update_settings_shifts_future_reminder_times(client, auth_headers):
    patch = client.patch(
        "/api/v1/user/settings",
        headers=auth_headers,
        json={"active_hours_start": "10:00:00", "active_hours_end": "12:00:00"},
    )
    assert patch.status_code == 200
    assert patch.json()["active_hours_start"] == "10:00:00"

    # P4 offset lands at 18:00, now outside the narrowed 10:00-12:00 active window,
    # so it should get clamped into that window rather than sitting at 18:00.
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Low priority task",
            "due_date": "in 30 days",
            "importance_level": 1,
            "estimated_effort": 5,
            "enable_reminder": True,
        },
    ).json()
    assert task["priority_label"] == "P4"
    trigger_hour = int(task["reminder"]["trigger_time"].split("T")[1][:2])
    assert 10 <= trigger_hour < 12


def test_update_notification_opt_out_prevents_reminder_creation(client, auth_headers):
    client.patch("/api/v1/user/settings", headers=auth_headers, json={"notification_opt_in": False})

    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task with opted-out user",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": True,
        },
    ).json()
    assert task["reminder"] is None
