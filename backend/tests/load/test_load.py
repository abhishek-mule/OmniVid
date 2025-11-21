"""
Load testing for OmniVid backend.
"""

import json
import time

import pytest
from locust import HttpUser, between, task
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_history, stats_printer


class OmniVidUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and store the token
        response = self.client.post(
            "/auth/login", json={"username": "testuser", "password": "testpassword"}
        )
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_videos(self):
        self.client.get("/api/videos", headers=self.headers)

    @task(2)
    def create_video(self):
        self.client.post(
            "/api/videos",
            headers={"Content-Type": "application/json", **self.headers},
            data=json.dumps(
                {
                    "title": "Load Test Video",
                    "description": "Test video created during load testing",
                }
            ),
        )

    @task(1)
    def get_user_profile(self):
        self.client.get("/api/users/me", headers=self.headers)


def test_load_test():
    """Run a basic load test scenario."""
    # This is a simplified test that would normally be run with locust
    # In a real scenario, you would run this with locust command line
    pass


# To run this test:
# 1. Install locust: pip install locust
# 2. Run: locust -f tests/load/test_load.py
# 3. Open http://localhost:8089 in your browser
# 4. Set number of users, spawn rate, and host
# 5. Start swarming!
