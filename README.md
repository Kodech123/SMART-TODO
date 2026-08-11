# DoSmart

Smart To-Do List with automatic task prioritization and an intelligent reminder system, built for university students managing academic and personal tasks.

## Stack

- **Backend:** FastAPI + PostgreSQL 15 + SQLAlchemy 2.0 + APScheduler + JWT auth
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
# 1. Postgres (Docker)
docker compose up -d

# 2. Backend
cd backend
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend API docs: http://localhost:8000/docs
Frontend: http://localhost:5173
