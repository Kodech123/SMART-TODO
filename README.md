# DoSmart

Smart To-Do List with automatic task prioritization and an intelligent reminder system, built for university students managing academic and personal tasks.

## Stack

- **Backend:** FastAPI + SQLite + SQLAlchemy 2.0 + APScheduler + JWT auth
- **Frontend:** React 18 + Redux Toolkit + Material-UI, built with Vite

## Repo layout

```
backend/    FastAPI app, SQLAlchemy models, Alembic migrations, pytest suite
frontend/   React SPA (Vite), Vitest + Cypress tests
docs/       architecture notes, API collection, load-test script, UAT materials
scripts/    dev helpers (db reset, seed data)
```

## Local setup

See `backend/README.md` and `frontend/README.md` for stack-specific setup instructions.

Quick start:

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend API docs: http://localhost:8000/docs
Frontend: http://localhost:5173

## Testing

```bash
# Backend unit/integration tests
cd backend && pytest

# Frontend unit tests
cd frontend && npm test

# Frontend E2E tests (needs the backend on :8000 and frontend on :5173 already running)
cd frontend && npm run cy:open   # interactive
cd frontend && npm run cy:run    # headless
```

## Deployment

The backend runs in Docker via Gunicorn with Uvicorn workers; the SQLite database file is
kept in a named volume (`dosmart_data`) so it survives container restarts/rebuilds.

```bash
docker compose up -d --build
```

This builds `backend/Dockerfile`, runs `alembic upgrade head` on startup, then serves the
API on http://localhost:8000. Before deploying anywhere but your own machine, override
`JWT_SECRET_KEY` in `backend/.env` — the checked-in value is a dev-only placeholder.

The frontend is a static Vite build (`npm run build` → `frontend/dist/`) meant to be served
by a static host or reverse proxy; it isn't containerized yet.
