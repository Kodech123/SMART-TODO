"""Load test for the DoSmart API.

Simulates a realistic student session: register/login once, then repeatedly
create tasks, list/filter them, view a task's score breakdown, check the
dashboard stats, and occasionally complete a task.

Usage:
    cd docs/load-test
    locust -f locustfile.py --host http://localhost:8000
    # or headless:
    locust -f locustfile.py --host http://localhost:8000 --headless -u 50 -r 10 --run-time 2m --csv=results
"""

import random
import uuid

from locust import HttpUser, between, task

TITLES = [
    "Submit assignment",
    "Study for exam",
    "Finish lab report",
    "Team meeting prep",
    "Doctor's appointment",
    "Buy groceries",
    "Call landlord",
    "Read chapter 5",
    "Group project sync",
    "Gym session",
]

DUE_DATES = ["tomorrow", "in 2 days", "in 3 days", "in 5 days", "next Friday", "in 10 days"]


class DoSmartUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        email = f"loadtest_{uuid.uuid4().hex[:12]}@example.com"
        response = self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePassword123", "display_name": "Load Test User"},
            name="/api/v1/auth/register",
        )
        token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})
        self.task_ids: list[int] = []

    @task(4)
    def create_task(self):
        response = self.client.post(
            "/api/v1/tasks",
            json={
                "title": random.choice(TITLES),
                "due_date": random.choice(DUE_DATES),
                "importance_level": random.randint(1, 5),
                "estimated_effort": random.randint(1, 5),
                "enable_reminder": True,
            },
            name="/api/v1/tasks [create]",
        )
        if response.status_code == 201:
            self.task_ids.append(response.json()["task_id"])

    @task(6)
    def list_tasks(self):
        self.client.get(
            "/api/v1/tasks?status=active&sort_by=priority_score",
            name="/api/v1/tasks [list]",
        )

    @task(3)
    def view_task_detail(self):
        if not self.task_ids:
            return
        task_id = random.choice(self.task_ids)
        self.client.get(f"/api/v1/tasks/{task_id}", name="/api/v1/tasks/[id] [detail+breakdown]")

    @task(3)
    def dashboard_stats(self):
        self.client.get("/api/v1/tasks/stats", name="/api/v1/tasks/stats")

    @task(1)
    def complete_task(self):
        if not self.task_ids:
            return
        task_id = self.task_ids.pop()
        self.client.put(f"/api/v1/tasks/{task_id}/complete", name="/api/v1/tasks/[id]/complete")

    @task(1)
    def list_reminders(self):
        self.client.get("/api/v1/reminders?status=pending", name="/api/v1/reminders")
