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
        pytest.skip("Live DB not available for lifecycle integration tests.")

    yield


@pytest.mark.integration
def test_sequential_test_clients_do_not_break_db_sessions():
    first_email = f"lifecycle-{uuid4()}@example.com"
    with TestClient(app) as first_client:
        first_response = first_client.post(
            "/api/v1/auth/register",
            json={"email": first_email, "password": "password123"},
        )
        assert first_response.status_code == 201

    second_email = f"lifecycle-{uuid4()}@example.com"
    with TestClient(app) as second_client:
        second_response = second_client.post(
            "/api/v1/auth/register",
            json={"email": second_email, "password": "password123"},
        )
        assert second_response.status_code == 201
