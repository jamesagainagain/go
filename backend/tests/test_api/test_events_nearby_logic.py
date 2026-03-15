from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.api.v1 import events as events_api


class _FakeResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def mappings(self) -> "_FakeResult":
        return self

    def all(self) -> list[dict[str, object]]:
        return self._rows


class _FakeSession:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.statement_text = ""
        self.params: dict[str, object] = {}

    async def execute(self, statement, params):  # noqa: ANN001
        self.statement_text = statement.text
        self.params = dict(params)
        return _FakeResult(self.rows)


@pytest.mark.api
@pytest.mark.asyncio
async def test_fetch_events_within_radius_uses_radius_meters():
    fake_session = _FakeSession(rows=[])
    await events_api._fetch_events_within_radius(
        session=fake_session,
        lat=51.5,
        lng=-0.12,
        radius_km=7.5,
        limit=10,
        now=datetime.now(UTC),
    )

    assert "ST_DWithin" in fake_session.statement_text
    assert fake_session.params["radius_meters"] == 7500.0
    assert fake_session.params["lat"] == 51.5
    assert fake_session.params["lng"] == -0.12


@pytest.mark.api
@pytest.mark.asyncio
async def test_events_nearby_maps_venue_coordinates_from_query(monkeypatch: pytest.MonkeyPatch):
    now = datetime.now(UTC)

    async def fake_fetch_events_within_radius(**kwargs):  # noqa: ANN003
        del kwargs
        return [
            {
                "id": uuid4(),
                "title": "Geo Event",
                "description": "Near event",
                "starts_at": now,
                "ends_at": None,
                "cost_pence": 0,
                "tags": ["community"],
                "tier": "structured",
                "venue_name": "Geo Venue",
                "venue_address": "Geo Street",
                "venue_lat": 51.5234,
                "venue_lng": -0.0789,
            }
        ]

    monkeypatch.setattr(events_api, "_fetch_events_within_radius", fake_fetch_events_within_radius)
    response = await events_api.events_nearby(
        lat=10.0,
        lng=20.0,
        radius_km=5,
        limit=1,
        current_user=object(),  # type: ignore[arg-type]
        session=object(),  # type: ignore[arg-type]
    )

    assert response.events
    assert response.events[0].venue is not None
    assert response.events[0].venue.lat == pytest.approx(51.5234)
    assert response.events[0].venue.lng == pytest.approx(-0.0789)
