from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.api.v1 import activations as activations_api
from app.models import Event, Opportunity, OpportunityTier, Venue
from app.schemas.opportunity import SocialProof


@pytest.mark.api
@pytest.mark.asyncio
async def test_opportunity_schema_uses_venue_coordinates_from_postgis(
    monkeypatch: pytest.MonkeyPatch,
):
    now = datetime.now(UTC)
    venue = Venue(name="Geo Venue", address="Geo Street")
    venue.id = uuid4()
    event = Event(
        title="Geo Event",
        starts_at=now + timedelta(minutes=30),
        tier=OpportunityTier.STRUCTURED,
        source="seed",
    )
    event.venue = venue
    event.cost_pence = 0
    event.source_url = "https://example.com/event"
    opportunity = Opportunity(
        tier=OpportunityTier.STRUCTURED,
        title="Geo Opportunity",
        body="A nearby opportunity",
        walk_minutes=8,
        travel_description="8 min walk",
        social_proof_text="3 others going solo",
        expires_at=now + timedelta(hours=2),
    )
    opportunity.event = event

    async def fake_load_venue_coordinates(**kwargs):  # noqa: ANN003
        del kwargs
        return 51.5234, -0.0789

    async def fake_build_social_proof(**kwargs):  # noqa: ANN003
        del kwargs
        return SocialProof(
            text="3 others going solo",
            total_expected=5,
            solo_count=3,
            familiar_face=False,
        )

    monkeypatch.setattr(activations_api, "_load_venue_coordinates", fake_load_venue_coordinates)
    monkeypatch.setattr(activations_api, "_build_social_proof", fake_build_social_proof)

    mapped = await activations_api._to_opportunity_schema(
        session=object(),  # type: ignore[arg-type]
        opportunity=opportunity,
        fallback_lat=10.0,
        fallback_lng=20.0,
    )

    assert mapped.venue.lat == pytest.approx(51.5234)
    assert mapped.venue.lng == pytest.approx(-0.0789)
