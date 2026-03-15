from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.services.openclaw import (
    DisabledOpenClawProvider,
    HttpOpenClawProvider,
    OpenClawSuggestion,
    build_openclaw_provider,
)


@pytest.mark.services
@pytest.mark.asyncio
async def test_openclaw_provider_is_disabled_by_default():
    provider = build_openclaw_provider(
        enabled=False,
        endpoint=None,
        api_token=None,
        timeout_seconds=4.0,
    )
    assert isinstance(provider, DisabledOpenClawProvider)
    suggestions = await provider.fetch_suggestions(city="london", hours_ahead=12)
    assert suggestions == []


@pytest.mark.services
def test_openclaw_provider_can_build_http_variant():
    provider = build_openclaw_provider(
        enabled=True,
        endpoint="https://openclaw.example/api/suggestions",
        api_token="token",
        timeout_seconds=2.0,
    )
    assert isinstance(provider, HttpOpenClawProvider)


@pytest.mark.services
@pytest.mark.asyncio
async def test_openclaw_http_provider_parses_valid_payload(monkeypatch: pytest.MonkeyPatch):
    provider = HttpOpenClawProvider(
        endpoint="https://openclaw.example/api/suggestions",
        api_token="token",
    )

    async def fake_fetch_payload(**kwargs):  # noqa: ANN003
        del kwargs
        return [
            {
                "title": "OpenClaw local nudge",
                "description": "Placeholder recommendation.",
                "starts_at": "2026-03-20T18:00:00Z",
                "location_text": "Shoreditch",
                "lat": 51.5247,
                "lng": -0.0794,
                "category": "micro_coordination",
                "source_url": "https://example.com/openclaw",
                "cost_hint": "Free",
                "tags": ["openclaw", "placeholder"],
            }
        ]

    monkeypatch.setattr(provider, "_fetch_payload", fake_fetch_payload)
    suggestions = await provider.fetch_suggestions(city="london", hours_ahead=12)

    assert len(suggestions) == 1
    first = suggestions[0]
    assert isinstance(first, OpenClawSuggestion)
    assert first.title == "OpenClaw local nudge"
    assert first.starts_at == datetime(2026, 3, 20, 18, 0, tzinfo=UTC)
