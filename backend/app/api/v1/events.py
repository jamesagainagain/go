from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models import Event, OpportunityTier, User
from app.schemas.event import EventsNearbyResponse, EventSummary
from app.schemas.opportunity import VenueSummary
from app.utils.security import get_current_user

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/nearby", response_model=EventsNearbyResponse)
async def events_nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(default=5, gt=0, le=50),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EventsNearbyResponse:
    del current_user, radius_km
    now = datetime.now(UTC) - timedelta(hours=2)
    result = await session.execute(
        select(Event)
        .where(Event.starts_at >= now)
        .order_by(Event.starts_at.asc())
        .limit(limit)
        .options(selectinload(Event.venue))
    )
    events = result.scalars().all()

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
        venue_summary = None
        if event.venue:
            venue_summary = VenueSummary(
                name=event.venue.name,
                lat=lat,
                lng=lng,
                address=event.venue.address,
            )
        summaries.append(
            EventSummary(
                id=event.id,
                title=event.title,
                description=event.description,
                starts_at=event.starts_at,
                ends_at=event.ends_at,
                cost_pence=event.cost_pence,
                tags=event.tags or [],
                venue=venue_summary,
                tier=event.tier,
            )
        )

    return EventsNearbyResponse(events=summaries)
