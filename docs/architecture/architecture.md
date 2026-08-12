# DoSmart Architecture

This document describes the system as implemented (not aspirationally) as of 2026-08-12.

## Three-tier architecture

```
┌───────────────────────────────────────────────────────────────┐
│ CLIENT LAYER                                                    │
│  React 18 SPA (Vite) — Dashboard, Task List/Detail/Form,        │
│  Reminders, Settings, Auth screens                               │
│  Service Worker (frontend/public/service-worker.js) — Web Push   │
│  notification receipt and click-to-task routing                  │
└───────────────────────────────────────────────────────────────┘
                              ↕ HTTPS / JSON (JWT bearer auth)
┌───────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER — FastAPI                                     │
│                                                                   │
│  Task Processing                                                 │
│   - date_parser.py: natural-language due dates (dateparser),     │
│     falls back to now+7d if unparseable                          │
│   - category_classifier.py: keyword-based auto-categorization    │
│     (Academic/Work/Health/Personal)                               │
│                                                                   │
│  Automatic Prioritization — priority_engine.py                   │
│   - Urgency / Importance / Deadline-proximity / Effort sub-scores │
│   - Weighted Priority Score (0-10), P1-P4 label                   │
│                                                                   │
│  Reminder & Notification Engine                                  │
│   - reminder_service.py: optimal reminder time per priority tier, │
│     clamped to the user's active hours                            │
│   - scheduler/: APScheduler BackgroundScheduler, SQLAlchemy       │
│     jobstore (persists jobs in the same DB, survives restarts)    │
│   - services/notification/: pluggable transport (log for dev,     │
│     webpush/pywebpush for production)                             │
│                                                                   │
│  REST API (routers/) — JWT-authenticated, /api/v1/*               │
└───────────────────────────────────────────────────────────────┘
                              ↕ SQLAlchemy 2.0 ORM
┌───────────────────────────────────────────────────────────────┐
│ DATA LAYER — SQLite (file-based, WAL mode)                       │
│  users, tasks, categories, reminders, push_subscriptions,        │
│  apscheduler_jobs                                                 │
└───────────────────────────────────────────────────────────────┘
```

## Technology stack (as installed, not aspirational)

| Layer | Technology | Version |
|---|---|---|
| Frontend | React | 18.3.1 |
| Frontend | Redux Toolkit | 2.12.0 |
| Frontend | Material-UI | 5.18.0 |
| Frontend | Vite | 7.3.6 (pinned — see note below) |
| Backend | FastAPI | 0.103.* |
| Backend | SQLAlchemy | 2.0.* |
| Backend | Alembic | 1.12.* |
| Backend | APScheduler | 3.10.4 |
| Backend | dateparser | 1.1.8 |
| Backend | pywebpush | 1.14.1 |
| Backend | PyJWT | 2.8.* |
| Database | SQLite | (Python stdlib `sqlite3`, WAL mode) |
| Deployment | Gunicorn + Uvicorn workers, Docker | — |

**Database note:** the original design targeted PostgreSQL 15 via Docker. SQLite was adopted as the permanent primary database (2026-08-12) — Docker Desktop was unreliable in this dev environment, and given DoSmart's expected load (single-user or small-scale academic use), a file-based database removes an operational dependency without changing the data model (SQLAlchemy makes the two portable; the CHECK constraints, indexes, and foreign keys defined in `alembic/versions/` work under both).

**Vite note:** pinned to 7.3.6 / `@vitejs/plugin-react` 5.2.0 rather than the latest 8.x. Vite 8's new Rolldown-based dependency pre-bundler double-wraps `@mui/icons-material`'s CommonJS default export, crashing every icon in the app. This is a known upstream regression, not an app bug.

## Automatic Prioritization Algorithm

Implemented in `backend/app/services/priority_engine.py`. Given `importance_level` (1-5, user input), `estimated_effort` (1-5, user input), and `due_date`:

```
days_remaining = (due_date - now).days          # floored at 0 for the formulas below;
                                                   # negative values still tracked for "overdue"
Urgency Score            = 10                              if overdue
                          = max(0, 10 - days_remaining/3)   otherwise
Importance Score         = importance_level × 2                          (range 2-10)
Deadline Proximity Score = max(0, 10 - days_remaining/5)                 (range 0-10, 0-50 day sensitivity)
Effort Score             = (6 - estimated_effort) × 2                    (range 2-10, inverted: lower effort ranks higher)

Priority Score = 0.35×Urgency + 0.35×Importance + 0.20×DeadlineProximity + 0.10×Effort
                 (clamped to [0, 10])

Priority Label: P1 (Critical) if score ≥ 8.0
                P2 (High)     if score ≥ 6.0
                P3 (Medium)   if score ≥ 4.0
                P4 (Low)      otherwise
```

Every task response includes a `scores.breakdown` object with the human-readable formula substitution for each sub-score (`GET /api/v1/tasks/{id}`), so the UI can show *why* a task got its priority rather than just the number. Scores are recomputed on create, on edit (`PATCH`), and periodically (`rescore_active_tasks`, every 30 minutes via APScheduler) since urgency/deadline-proximity drift with time even without user edits.

## Reminder & Notification Engine

Reminder timing (`reminder_service.calculate_optimal_reminder_time`) is a fixed offset per priority tier, then clamped into the user's configured active hours (default 08:00-22:00):

| Priority | Offset before due date | Target hour |
|---|---|---|
| P1 | 1 day | — (same time as due date, minus 1 day) |
| P2 | 2 days | 09:00 |
| P3 | 3 days | 14:00 |
| P4 | 5 days | 18:00 |

If the computed time falls outside active hours it's clamped to the boundary; if it would fall in the past (very-near-term due dates) it fires one minute from now instead of being silently dropped.

Each reminder becomes a persistent APScheduler job (`SQLAlchemyJobStore`, stored in the same database, table `apscheduler_jobs`) so scheduled reminders survive an application restart. Completing or deleting a task cancels its pending reminder's job. Delivery goes through a pluggable `NotificationTransport`: `log` (prints to server log, used in dev/tests) or `webpush` (real Web Push via VAPID keys and `pywebpush`), selected by the `NOTIFICATION_TRANSPORT` env var.

## Data model

5 core tables (see `backend/alembic/versions/b0354546fbb7_initial_schema.py` for the authoritative schema):

- **users** — email, bcrypt password_hash, display_name, `active_hours_start`/`active_hours_end` (reminder timing), `notification_opt_in`, `default_reminder_minutes`
- **tasks** — title, description, `category_id` (nullable, `SET NULL` on category delete), `importance_level`/`estimated_effort` (1-5, CHECK-constrained), `due_date`, the 4 sub-scores + `priority_score` + `priority_label` (P1-P4, CHECK-constrained), `status` (active/completed/deleted), timestamps
- **categories** — per-user, unique `(user_id, category_name)`, `color_hex`, `icon_name`; four defaults seeded per new user (Academic/Work/Personal/Health)
- **reminders** — `task_id`, `trigger_time`, `job_id` (unique, links to the APScheduler job), `status` (pending/delivered/cancelled/failed)
- **push_subscriptions** — Web Push `endpoint` + `p256dh`/`auth` keys per user

Indexes: `(user_id, status)`, `(user_id, priority_score)`, `(user_id, due_date)` on tasks; `(user_id, trigger_time)` on reminders — matching the query patterns the API actually uses (list-by-status, sort-by-priority, list-by-due-date, and the reminder scheduler's lookups).

## REST API surface

JWT-authenticated (`PyJWT`, `HS256`, 24h expiry by default), routed under `/api/v1/`:

- `auth`: register, login, logout
- `tasks`: create (auto-computes priority + schedules reminder), list (paginated/filtered/sorted), get (includes score breakdown), patch (recalculates priority + reschedules reminder), complete (cancels reminder), delete, `/stats` (dashboard aggregates: counts, completion rate, priority distribution, 7-day completion trend)
- `reminders`: list pending, snooze
- `categories`: CRUD
- `user`: get/patch settings (active hours, notification opt-in)
- `push`: subscribe/unsubscribe

Full machine-readable spec: `docs/api/openapi.json`. Example requests: `docs/api/DoSmart.postman_collection.json`.

## Testing & CI

- Backend: pytest, unit (`priority_engine`, `date_parser`, `category_classifier`, `reminder_service`) + integration (full API flows against a real SQLite DB) — 64 tests
- Frontend: Vitest + React Testing Library — 14 tests
- E2E: Cypress, one spec covering register → create task → view score breakdown → complete → logout/login persistence
- CI: GitHub Actions (`.github/workflows/ci.yml`) runs all three tiers on every push/PR to `main`
- Load: see `docs/load-test/`

## Deployment

`backend/Dockerfile` runs the API via Gunicorn + Uvicorn workers, applying Alembic migrations on container start. `docker-compose.yml` persists the SQLite file in a named volume so data survives container rebuilds. The frontend is a static Vite build (`npm run build`) intended to be served by a static host or reverse proxy; it is not yet containerized.
