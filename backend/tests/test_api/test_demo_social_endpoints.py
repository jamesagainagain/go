from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_demo_event_attendees_endpoint_returns_profiles():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/events/demo/attendees",
            params={
                "event_key": "demo-test-event-1",
                "title": "After-work drawing social",
                "tags": "art,community",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["event_key"] == "demo-test-event-1"
    assert payload["event_title"] == "After-work drawing social"
    assert payload["total_expected"] >= 1
    assert isinstance(payload["attendees"], list)
    assert payload["attendees"]
    first = payload["attendees"][0]
    assert first["display_name"]
    assert first["interests"]
