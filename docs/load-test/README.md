# Load testing

- **`locustfile.py`** — Locust script simulating a realistic student session (register, create/list/view/complete tasks, check reminders and stats). Usage instructions are in its docstring.
- **`results.md`** — a real run against this repo's backend on 2026-08-12, including a bug (SQLAlchemy connection pool exhaustion) found and fixed as a direct result of running it.
- **`results_*.csv`** — raw Locust output backing `results.md`.

Re-run it yourself:

```bash
cd backend && uvicorn app.main:app --port 8000 &
cd docs/load-test
locust -f locustfile.py --host http://localhost:8000              # interactive web UI on :8089
locust -f locustfile.py --host http://localhost:8000 \
  --headless -u 50 -r 10 --run-time 90s --csv=results             # headless, matches results.md
```
