from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"check_same_thread": False})


# SQLite only allows one writer at a time; the app's own session and APScheduler's
# jobstore (sharing this engine, see scheduler.py) can otherwise collide with
# "database is locked". WAL mode + a busy timeout let the second writer wait instead
# of failing immediately.
@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=10000")
    # SQLite ignores FK constraints (e.g. categories' ON DELETE SET NULL) unless
    # explicitly enabled per-connection.
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
