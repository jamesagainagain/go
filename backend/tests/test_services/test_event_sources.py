from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.services.event_sources import (
    OpenClawEventSourceAdapter,
    PlacesCatalogAdapter,
    build_default_event_source_adapters,
)
from app.services.openclaw import DisabledOpenClawProvider


@pytest.mark.services
def test_default_event_source_adapters_include_places_catalog():
    adapters = build_default_event_source_adapters(
        include_places_catalog=True,
        openclaw_enabled=False,
        openclaw_endpoint=None,
        openclaw_api_token=None,
        openclaw_timeout_seconds=4.0,
    )
    assert len(adapters) == 2
    assert isinstance(adapters[0], PlacesCatalogAdapter)
    assert isinstance(adapters[1], OpenClawEventSourceAdapter)

    empty = build_default_event_source_adapters(
        include_places_catalog=False,
        openclaw_enabled=False,
        openclaw_endpoint=None,
        openclaw_api_token=None,
        openclaw_timeout_seconds=4.0,
    )
    assert len(empty) == 1
    assert isinstance(empty[0], OpenClawEventSourceAdapter)


@pytest.mark.services
@pytest.mark.asyncio
async def test_places_catalog_adapter_generates_events(tmp_path: Path):
    catalog_path = tmp_path / "places.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "name": "Demo Museum",
                    "address": "Test St, London",
                    "borough": "Camden",
                    "lat": 51.52,
                    "lng": -0.12,
                    "category": "museum",
                    "tags": ["culture"],
                    "source_url": "https://museum.example",
                    "cost_hint": "Free",
                },
                {
                    "name": "Demo Restaurant",
                    "address": "Food St, London",
                    "borough": "Hackney",
                    "lat": 51.54,
                    "lng": -0.08,
                    "category": "restaurant",
                    "tags": ["food"],
                    "source_url": "https://restaurant.example",
                    "cost_hint": "£20",
                },
            ]
        ),
        encoding="utf-8",
    )
    adapter = PlacesCatalogAdapter(catalog_path=catalog_path)
    events = await adapter.fetch_events(city="london", radius_km=5, hours_ahead=24)
    assert len(events) == 2

    first = events[0]
    second = events[1]
    assert first.source_name == "local_places"
    assert second.source_name == "local_places"
    assert "museum" in (first.tags_raw or [])
    assert "restaurant" in (second.tags_raw or [])
    assert isinstance(first.start_time, datetime)
    assert first.start_time.tzinfo is UTC


@pytest.mark.services
@pytest.mark.asyncio
async def test_places_catalog_adapter_is_london_only(tmp_path: Path):
    catalog_path = tmp_path / "places.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "name": "Demo Cafe",
                    "address": "Cafe St, London",
                    "lat": 51.5,
                    "lng": -0.1,
                    "category": "cafe",
                }
            ]
        ),
        encoding="utf-8",
    )
    adapter = PlacesCatalogAdapter(catalog_path=catalog_path)
    events = await adapter.fetch_events(city="manchester", radius_km=5, hours_ahead=24)
    assert events == []


@pytest.mark.services
@pytest.mark.asyncio
async def test_openclaw_framework_adapter_is_non_blocking_when_disabled():
    adapter = OpenClawEventSourceAdapter(provider=DisabledOpenClawProvider())
    events = await adapter.fetch_events(city="london", radius_km=5, hours_ahead=24)
    assert events == []
