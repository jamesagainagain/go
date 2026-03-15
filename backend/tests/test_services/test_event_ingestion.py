from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.services.event_ingestion import (
    EventIngestionService,
    RawEvent,
    parse_cost_to_pence,
)
from app.services.geocoding import GeocodeResult


class FakeGeocoder:
    async def geocode(self, location_text: str) -> GeocodeResult | None:
        if "shoreditch" in location_text.lower():
            return GeocodeResult(lat=51.5247, lng=-0.0794, source="test")
        return None


class FakeAdapter:
    def __init__(self, name: str, payload: list[RawEvent]) -> None:
        self.name = name
        self._payload = payload

    async def fetch_events(self, city: str, radius_km: float, hours_ahead: int) -> list[RawEvent]:
        del city, radius_km, hours_ahead
        return self._payload


class FlakyAdapter:
    def __init__(self, *, name: str = "flaky") -> None:
        self.name = name
        self.call_count = 0

    async def fetch_events(self, city: str, radius_km: float, hours_ahead: int) -> list[RawEvent]:
        del city, radius_km, hours_ahead
        self.call_count += 1
        if self.call_count == 1:
            raise TimeoutError("transient timeout")
        return [
            RawEvent(
                source_name="flaky",
                title="Recovered Event",
                start_time=datetime.now(UTC) + timedelta(hours=1),
                location_text="Shoreditch",
            )
        ]


@pytest.mark.services
@pytest.mark.asyncio
async def test_ingestion_normalizes_and_enriches_events():
    adapter = FakeAdapter(
        "seed",
        [
            RawEvent(
                source_name="eventbrite",
                title="Life Drawing Social",
                description="Beginner-friendly drop-in art evening.",
                start_time=datetime.now(UTC) + timedelta(hours=2),
                location_text="Shoreditch Arts Club",
                cost_text="£7.50",
                tags_raw=["Art", " Evening "],
                source_url="https://example.com/events/1",
            )
        ],
    )
    service = EventIngestionService(adapters=[adapter], geocoder=FakeGeocoder())

    result = await service.fetch_normalized_events(city="london", radius_km=5, hours_ahead=12)

    assert result.source_errors == {}
    assert len(result.events) == 1
    event = result.events[0]
    assert event.lat == pytest.approx(51.5247)
    assert event.lng == pytest.approx(-0.0794)
    assert event.cost_pence == 750
    assert "art" in event.tags
    assert event.solo_friendly_score > 0.5


@pytest.mark.services
@pytest.mark.asyncio
async def test_ingestion_dedupes_similar_events():
    starts_at = datetime.now(UTC) + timedelta(hours=3)
    adapter = FakeAdapter(
        "seed",
        [
            RawEvent(
                source_name="meetup",
                title="Canal Walk and Coffee",
                start_time=starts_at,
                lat=51.5200,
                lng=-0.0700,
            ),
            RawEvent(
                source_name="eventbrite",
                title="Canal Walk & Coffee",
                start_time=starts_at + timedelta(minutes=10),
                lat=51.5203,
                lng=-0.0702,
            ),
        ],
    )
    service = EventIngestionService(adapters=[adapter], geocoder=FakeGeocoder())

    result = await service.fetch_normalized_events(city="london", radius_km=5, hours_ahead=24)

    assert len(result.events) == 1


@pytest.mark.services
@pytest.mark.asyncio
async def test_provider_registry_and_retry_behavior():
    flaky = FlakyAdapter()
    service = EventIngestionService(geocoder=FakeGeocoder())
    service.register_provider("openclaw", flaky)

    result = await service.fetch_normalized_events(city="london", radius_km=5, hours_ahead=6)

    assert "openclaw" in service.available_providers()
    assert flaky.call_count == 2
    assert len(result.events) == 1


def test_parse_cost_to_pence_handles_common_formats():
    assert parse_cost_to_pence("Free") == 0
    assert parse_cost_to_pence("5 GBP") == 500
    assert parse_cost_to_pence("£12.50") == 1250
    assert parse_cost_to_pence("250p") == 250
