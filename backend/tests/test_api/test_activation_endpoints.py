from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEST_DB_URL = os.environ.get(
    "TEST_MIGRATION_DB_URL",
    "postgresql+asyncpg://firstmove:password@localhost:5432/firstmove",
)


def _run_alembic(*args: str) -> int:
    env = os.environ.copy()
    env["SUPABASE_DB_URL"] = TEST_DB_URL
    env["REDIS_URL"] = env.get("REDIS_URL", "redis://localhost:6379/0")
    env["SECRET_KEY"] = env.get("SECRET_KEY", "test-secret")
    process = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return process.returncode


@pytest.fixture(scope="module", autouse=True)
def setup_live_db() -> Generator[None, None, None]:
    os.environ["SUPABASE_DB_URL"] = TEST_DB_URL
    os.environ["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    os.environ["SECRET_KEY"] = os.environ.get("SECRET_KEY", "test-secret")
    get_settings.cache_clear()

    if _run_alembic("upgrade", "head") != 0:
        pytest.skip("Live DB not available for activation API integration tests.")

    yield


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def _register_user(client: TestClient) -> dict[str, str]:
    email = f"activation-{uuid4()}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201
    payload = response.json()
    return {
        "email": email,
        "access_token": payload["access_token"],
    }


def test_activation_check_and_current(client: TestClient):
    user = _register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    check_response = client.post(
        "/api/v1/activations/check",
        headers=headers,
        json={"lat": 51.5074, "lng": -0.1278},
    )
    assert check_response.status_code == 200
    check_payload = check_response.json()
    assert check_payload["activation_id"] is not None
    assert check_payload["opportunity"]["title"]

    current_response = client.get("/api/v1/activations/current", headers=headers)
    assert current_response.status_code == 200
    current_payload = current_response.json()
    assert current_payload["activation_id"] == check_payload["activation_id"]


def test_activation_respond_feedback_and_history(client: TestClient):
    user = _register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    check_response = client.post("/api/v1/activations/check", headers=headers, json={})
    activation_id = check_response.json()["activation_id"]

    respond_response = client.post(
        f"/api/v1/activations/{activation_id}/respond",
        headers=headers,
        json={"response": "accepted"},
    )
    assert respond_response.status_code == 200

    feedback_response = client.post(
        f"/api/v1/activations/{activation_id}/feedback",
        headers=headers,
        json={"attended": True, "rating": 5, "feedback_text": "Great energy"},
    )
    assert feedback_response.status_code == 200

    history_response = client.get(
        "/api/v1/activations/history?limit=5&offset=0",
        headers=headers,
    )
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["total"] >= 1
    assert history_payload["items"][0]["id"] == activation_id
    assert history_payload["items"][0]["response"] == "accepted"
    assert history_payload["items"][0]["attended"] is True


def test_events_nearby_returns_list(client: TestClient):
    user = _register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    response = client.get(
        "/api/v1/events/nearby?lat=51.5074&lng=-0.1278&radius_km=5&limit=1",
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["events"]) <= 1
    assert payload["events"]


def test_push_subscribe_idempotent(client: TestClient):
    user = _register_user(client)
    headers = {"Authorization": f"Bearer {user['access_token']}"}
    subscription_payload = {
        "endpoint": "https://push.example.test/subscription/123",
        "expirationTime": None,
        "keys": {"p256dh": "abc", "auth": "def"},
    }

    first_response = client.post(
        "/api/v1/push/subscribe",
        headers=headers,
        json=subscription_payload,
    )
    second_response = client.post(
        "/api/v1/push/subscribe",
        headers=headers,
        json=subscription_payload,
    )
    assert first_response.status_code == 200
    assert second_response.status_code == 200


def test_calendar_webhook_validation(client: TestClient):
    invalid_response = client.post("/api/v1/webhooks/calendar", json={"event_type": "updated"})
    assert invalid_response.status_code == 400

    valid_response = client.post(
        "/api/v1/webhooks/calendar",
        json={"resource_id": "calendar-123", "event_type": "updated"},
    )
    assert valid_response.status_code == 200
