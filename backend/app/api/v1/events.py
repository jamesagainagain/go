from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import OpportunityTier, User
from app.schemas.event import EventsNearbyResponse, EventSummary
from app.schemas.opportunity import VenueSummary
from app.utils.security import get_optional_user

router = APIRouter(prefix="/events", tags=["events"])


async def _fetch_events_within_radius(
    *,
    session: AsyncSession,
    lat: float,
    lng: float,
    radius_km: float,
    limit: int,
    now: datetime,
) -> list[dict[str, object]]:
    query = text(
        """
        SELECT
            e.id,
            e.title,
            e.description,
            e.starts_at,
            e.ends_at,
            e.cost_pence,
            e.tags,
            e.tier,
            v.name AS venue_name,
            v.address AS venue_address,
            ST_Y(v.location::geometry) AS venue_lat,
            ST_X(v.location::geometry) AS venue_lng
        FROM events e
        JOIN venues v ON v.id = e.venue_id
        WHERE e.starts_at >= :now
          AND v.location IS NOT NULL
          AND ST_DWithin(
            v.location,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
            :radius_meters
          )
        ORDER BY e.starts_at ASC
        LIMIT :limit
        """
    )
    result = await session.execute(
        query,
        {
            "now": now,
            "lat": lat,
            "lng": lng,
            "radius_meters": radius_km * 1000,
            "limit": limit,
        },
    )
    return [dict(row) for row in result.mappings().all()]


@router.get("/nearby", response_model=EventsNearbyResponse)
async def events_nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(default=5, gt=0, le=50),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_db_session),
) -> EventsNearbyResponse:
    del current_user
    now = datetime.now(UTC) - timedelta(hours=2)
    events = await _fetch_events_within_radius(
        session=session,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
        now=now,
    )

    if not events:
        fallback_event = EventSummary(
            id=uuid4(),
            title="Community walk nearby",
            description="A low-friction solo-friendly walk happening soon.",
            starts_at=datetime.now(UTC) + timedelta(minutes=45),
            ends_at=None,
            cost_pence=0,
            tags=["outdoors", "wellness"],
            venue=VenueSummary(name="Nearby meetup point", lat=lat, lng=lng, address=None),
            tier=OpportunityTier.SOLO_NUDGE,
        )
        return EventsNearbyResponse(events=[fallback_event])

    summaries: list[EventSummary] = []
    for event in events:
        venue_summary = VenueSummary(
            name=str(event["venue_name"]),
            lat=float(event["venue_lat"]),
            lng=float(event["venue_lng"]),
            address=str(event["venue_address"]) if event["venue_address"] is not None else None,
        )
        summaries.append(
            EventSummary(
                id=event["id"],
                title=str(event["title"]),
                description=event["description"],
                starts_at=event["starts_at"],
                ends_at=event["ends_at"],
                cost_pence=event["cost_pence"],
                tags=event["tags"] or [],
                venue=venue_summary,
                tier=event["tier"],
            )
        )

    return EventsNearbyResponse(events=summaries)
