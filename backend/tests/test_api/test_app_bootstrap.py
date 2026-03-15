from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v1_router_prefix_is_registered(client: TestClient):
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
