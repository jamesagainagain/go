from __future__ import annotations

import pytest

from app.services.event_sources import TicketmasterAdapter, build_default_event_source_adapters


@pytest.mark.services
def test_default_event_source_adapters_include_ticketmaster():
    adapters = build_default_event_source_adapters(ticketmaster_api_key="test-key")
    assert len(adapters) == 1
    assert isinstance(adapters[0], TicketmasterAdapter)

    empty = build_default_event_source_adapters(ticketmaster_api_key=None)
    assert empty == []


@pytest.mark.services
@pytest.mark.asyncio
async def test_ticketmaster_adapter_parses_events(monkeypatch: pytest.MonkeyPatch):
    adapter = TicketmasterAdapter(api_key="test-key")

    async def fake_fetch_payload(**kwargs):  # noqa: ANN003
        del kwargs
        return {
            "_embedded": {
                "events": [
                    {
                        "name": "London Open Mic Night",
                        "url": "https://example.com/event-1",
                        "info": "A beginner-friendly open mic for solo attendees.",
                        "dates": {
                            "start": {"dateTime": "2026-03-20T19:00:00Z"},
                            "end": {"dateTime": "2026-03-20T21:00:00Z"},
                        },
                        "priceRanges": [{"min": 12.5, "currency": "GBP"}],
                        "classifications": [
                            {"segment": {"name": "Music"}, "genre": {"name": "Alternative"}}
                        ],
                        "_embedded": {
                            "venues": [
                                {
                                    "name": "Southbank Centre",
                                    "postalCode": "SE1 8XX",
                                    "address": {"line1": "Belvedere Rd"},
                                    "city": {"name": "London"},
                                    "location": {"latitude": "51.5068", "longitude": "-0.1167"},
                                }
                            ]
                        },
                    }
                ]
            }
        }

    monkeypatch.setattr(adapter, "_fetch_payload", fake_fetch_payload)
    events = await adapter.fetch_events(city="london", radius_km=5, hours_ahead=24)
    assert len(events) == 1

    event = events[0]
    assert event.source_name == "ticketmaster"
    assert event.title == "London Open Mic Night"
    assert event.start_time == "2026-03-20T19:00:00Z"
    assert event.location_text == "Southbank Centre, Belvedere Rd, London, SE1 8XX"
    assert event.lat == pytest.approx(51.5068)
    assert event.lng == pytest.approx(-0.1167)
    assert event.cost_text == "£12.50"
    assert event.tags_raw is not None
    assert "music" in event.tags_raw
