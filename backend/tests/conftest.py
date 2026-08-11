import os

from dotenv import load_dotenv

load_dotenv()  # picks up TEST_DATABASE_URL from backend/.env, same precedence app.core.config uses

# Point the app at the test database *before* app.core.config is imported anywhere,
# so the module-level SQLAlchemy engine and the APScheduler jobstore both bind to it.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg2://postgres:devpassword@localhost:5432/dosmart_test"
)
os.environ["NOTIFICATION_TRANSPORT"] = "log"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture()
def db_session(_reset_db):
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def client(_reset_db):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "student@example.com", "password": "SecurePassword123", "display_name": "Test Student"},
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
