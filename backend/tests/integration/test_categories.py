def test_list_categories_returns_defaults(client, auth_headers):
    response = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    names = {c["category_name"] for c in response.json()}
    assert names == {"Academic", "Work", "Personal", "Health"}


def test_create_update_delete_custom_category(client, auth_headers):
    create = client.post(
        "/api/v1/categories", headers=auth_headers, json={"category_name": "Side Projects", "color_hex": "#123456"}
    )
    assert create.status_code == 201, create.text
    category_id = create.json()["category_id"]
    assert create.json()["is_default"] is False

    update = client.patch(
        f"/api/v1/categories/{category_id}", headers=auth_headers, json={"color_hex": "#abcdef"}
    )
    assert update.status_code == 200
    assert update.json()["color_hex"] == "#abcdef"

    delete = client.delete(f"/api/v1/categories/{category_id}", headers=auth_headers)
    assert delete.status_code == 204


def test_cannot_create_duplicate_category_name(client, auth_headers):
    response = client.post("/api/v1/categories", headers=auth_headers, json={"category_name": "Academic"})
    assert response.status_code == 409


def test_cannot_delete_default_category(client, auth_headers):
    categories = client.get("/api/v1/categories", headers=auth_headers).json()
    default_category = next(c for c in categories if c["is_default"])

    response = client.delete(f"/api/v1/categories/{default_category['category_id']}", headers=auth_headers)
    assert response.status_code == 400


def test_deleting_category_uncategorizes_its_tasks(client, auth_headers):
    category = client.post("/api/v1/categories", headers=auth_headers, json={"category_name": "Temp"}).json()
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Task in temp category",
            "category": "Temp",
            "due_date": "in 5 days",
            "importance_level": 3,
            "estimated_effort": 3,
            "enable_reminder": False,
        },
    ).json()
    assert task["category"] == "Temp"

    client.delete(f"/api/v1/categories/{category['category_id']}", headers=auth_headers)

    refreshed = client.get(f"/api/v1/tasks/{task['task_id']}", headers=auth_headers).json()
    assert refreshed["category"] is None
