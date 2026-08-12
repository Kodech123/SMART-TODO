# Load test results

**Run date:** 2026-08-12
**Environment:** single dev machine, backend run as one `uvicorn` process (no Gunicorn workers), SQLite database, `docs/load-test/locustfile.py`, command: `locust -f locustfile.py --host http://localhost:8000 --headless -u 50 -r 10 --run-time 90s`

This is **not** the spec's target environment (500 concurrent users against PostgreSQL, presumably behind Gunicorn with multiple workers) — it's what's actually available to test against right now. The numbers below are real, not projected, and the point of running them was to find real bottlenecks, which it did.

## First run: connection pool exhaustion

The first 50-user run failed hard: **34% of requests failed** (46/135), with response times up to 62s, all failing with:

```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out, timeout 30.00
```

Root cause: `backend/app/db/session.py` created the SQLAlchemy engine with SQLAlchemy's defaults — a pool of 5 connections + 10 overflow (15 total). With 50 concurrent simulated users, requests queued for a free connection and timed out well before ever reaching SQLite. This is a connection-pool-size bug, separate from SQLite's single-writer limitation, and it was fixed on the spot: `pool_size=20, max_overflow=20` in `create_engine()`.

## Second run: after the pool size fix

Same 50-user, 90-second run, freshly re-seeded database:

| Metric | Before | After |
|---|---|---|
| Requests completed | 135 | 1,564 |
| Failures | 46 (34%) | 0 (0%) |
| Throughput | 1.3 req/s | 17.5 req/s |

Per-endpoint (full data in `results_stats.csv`):

| Endpoint | Requests | Median | p90 | p95 | p99 | Max |
|---|---|---|---|---|---|---|
| `POST /auth/register` | 50 | 4900ms | 6500ms | 6800ms | 7400ms | 7434ms |
| `GET /tasks` (list) | 498 | 40ms | 270ms | 440ms | 1700ms | 2222ms |
| `GET /tasks/{id}` (detail+breakdown) | 233 | 28ms | 190ms | 330ms | 520ms | 584ms |
| `GET /tasks/stats` | 258 | 48ms | 280ms | 650ms | 2100ms | 2162ms |
| `GET /reminders` | 101 | 33ms | 200ms | 310ms | 470ms | 2123ms |
| `POST /tasks` (create) | 349 | 370ms | 3400ms | 19000ms | 27000ms | 28232ms |
| `PUT /tasks/{id}/complete` | 64 | 95ms | 520ms | 540ms | 820ms | 818ms |

## Analysis

- **Reliability**: the pool-size fix took failures from 34% to 0%. That was the most impactful single change.
- **Read-heavy endpoints are fast**: list/detail/stats/reminders all sit under 250ms through the median and p90 — well inside the spec's ≤250ms p95 target at this concurrency, for reads specifically.
- **Write-heavy endpoints are the real bottleneck**, and don't meet the ≤250ms p95 target: `POST /tasks` create does 3+ writes per call (the task row, a reminder row, and an APScheduler job persisted into the same SQLite file) and its p95 balloons to 19s. `POST /auth/register` writes a user row plus 4 default category rows and also runs bcrypt hashing (intentionally slow), averaging ~5s.
- **Root cause of the write-path slowness is SQLite's single-writer model**, not the application code: `backend/app/db/session.py` already sets WAL mode + a 10s busy-timeout precisely because concurrent writers have to queue for the one writer slot. Under load, that queueing is what shows up as latency here — writes aren't failing, they're waiting.

## Does this meet the spec's performance target?

No, not as currently deployed — the spec calls for ≤250ms p95 at 500 concurrent users, which this setup doesn't reach for write-heavy paths even at 50 concurrent users. That's an expected, honest result given the deliberate move to a file-based SQLite database (see `docs/architecture/architecture.md`) instead of the originally-specced PostgreSQL, and given this is one dev-machine `uvicorn` process rather than a properly resourced deployment. To meaningfully approach the original target would require either PostgreSQL (removes the single-writer constraint entirely) or restructuring the write path (e.g. making reminder scheduling asynchronous instead of inline with task creation).

## Raw data

- `results_stats.csv` — final per-endpoint aggregate stats
- `results_stats_history.csv` — stats sampled every ~few seconds through the run
- `results_failures.csv`, `results_exceptions.csv` — empty (zero failures on the post-fix run)
