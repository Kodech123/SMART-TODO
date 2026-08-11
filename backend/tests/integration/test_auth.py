def test_register_creates_user_and_default_categories(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "SecurePassword123", "display_name": "New Student"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["access_token"]

    categories = client.get(
        "/api/v1/categories", headers={"Authorization": f"Bearer {body['access_token']}"}
    ).json()
    category_names = {c["category_name"] for c in categories}
    assert category_names == {"Academic", "Work", "Personal", "Health"}


def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "password": "SecurePassword123", "display_name": "Dup"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_login_success_and_failure(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "SecurePassword123", "display_name": "Login"},
    )

    ok = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "SecurePassword123"})
    assert ok.status_code == 200
    assert "access_token" in ok.json()

    bad = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "WrongPassword"})
    assert bad.status_code == 401


def test_protected_route_without_token_is_401(client):
    response = client.get("/api/v1/tasks")
    assert response.status_code == 403 or response.status_code == 401


def test_protected_route_with_token_works(client, auth_headers):
    response = client.get("/api/v1/tasks", headers=auth_headers)
    assert response.status_code == 200
