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
        pytest.skip("Live DB not available for auth/user API integration tests.")

    yield


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def _register_user(client: TestClient, *, email: str, password: str = "password123") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": "First Move",
            "preferences": [{"category": "art", "weight": 0.8, "explicit": True}],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_register_and_conflict(client: TestClient):
    email = f"user-{uuid4()}@example.com"
    first_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert second_response.status_code == 409


def test_login_success_and_invalid_credentials(client: TestClient):
    email = f"user-{uuid4()}@example.com"
    _register_user(client, email=email)

    success_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert success_response.status_code == 200
    assert "access_token" in success_response.json()

    invalid_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong"},
    )
    assert invalid_response.status_code == 401


def test_me_update_and_location(client: TestClient):
    email = f"user-{uuid4()}@example.com"
    register_payload = _register_user(client, email=email)
    token = register_payload["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

    update_response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"display_name": "Updated Name", "willingness_radius_km": 7.5},
    )
    assert update_response.status_code == 200
    assert update_response.json()["display_name"] == "Updated Name"

    location_response = client.post(
        "/api/v1/users/me/location",
        headers=headers,
        json={"lat": 51.5007, "lng": -0.1246},
    )
    assert location_response.status_code == 200
    assert location_response.json()["status"] == "ok"
