from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, categories, push, reminders, tasks, user
from app.scheduler.scheduler import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="DoSmart API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    # Vite picks the next free port (5174, 5175, ...) whenever 5173 is already taken by
    # another dev server, so a fixed allowlist of ports constantly falls out of date in
    # local dev. This regex covers any localhost/127.0.0.1 port; it never matches a real
    # production domain, so allow_origins above is still what governs non-local deploys.
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(tasks.router)
app.include_router(reminders.router)
app.include_router(user.router)
app.include_router(push.router)


@app.api_route("/health", methods=["GET", "HEAD"])
def health() -> dict[str, str]:
    return {"status": "ok"}
