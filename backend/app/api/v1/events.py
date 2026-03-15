from __future__ import annotations

import json
from functools import lru_cache
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid4, uuid5

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import OpportunityTier, User
from app.schemas.event import EventAttendee, EventAttendeesResponse, EventsNearbyResponse, EventSummary
from app.schemas.opportunity import VenueSummary
from app.services.demo_social_graph import DemoSocialGraphService
from app.utils.geo import haversine_km
from app.utils.security import get_current_user

router = APIRouter(prefix="/events", tags=["events"])
DEMO_PLACES_PATH = Path(__file__).resolve().parents[4] / "data" / "seeds" / "london_local_places.json"


@lru_cache
def get_demo_social_graph_service() -> DemoSocialGraphService:
    return DemoSocialGraphService()


@lru_cache
def get_demo_places_catalog() -> list[dict[str, object]]:
    try:
        payload = json.loads(DEMO_PLACES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


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


async def _build_events_nearby_response(
    *,
    session: AsyncSession,
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(default=5, gt=0, le=50),
    limit: int = Query(default=20, ge=1, le=100),
) -> EventsNearbyResponse:
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


def _to_demo_tier(category: str) -> OpportunityTier:
    if category in {"park", "outdoors"}:
        return OpportunityTier.SOLO_NUDGE
    if category in {"food_market", "cafe"}:
        return OpportunityTier.MICRO_COORDINATION
    if category in {"gallery", "museum"}:
        return OpportunityTier.RECURRING_PATTERN
    return OpportunityTier.STRUCTURED


def _parse_cost_hint_to_pence(cost_hint: object) -> int:
    if not cost_hint:
        return 0
    text = str(cost_hint).strip().lower()
    if text == "free":
        return 0
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return 0
    return int(digits) * 100


def _build_demo_seed_events(
    *,
    lat: float,
    lng: float,
    radius_km: float,
    limit: int,
) -> EventsNearbyResponse:
    places = get_demo_places_catalog()
    now = datetime.now(UTC).replace(second=0, microsecond=0)
    scored: list[tuple[float, EventSummary]] = []
    for index, place in enumerate(places):
        place_lat = place.get("lat")
        place_lng = place.get("lng")
        if not isinstance(place_lat, (int, float)) or not isinstance(place_lng, (int, float)):
            continue
        distance = haversine_km(lat, lng, float(place_lat), float(place_lng))
        if distance > radius_km + 1.5:
            continue

        name = str(place.get("name", "London place"))
        category = str(place.get("category", "community")).strip().lower()
        tags = [
            str(tag).strip().lower()
            for tag in (place.get("tags") or [])
            if isinstance(tag, str) and tag.strip()
        ]
        event_summary = EventSummary(
            id=uuid5(NAMESPACE_DNS, f"demo-place:{name}"),
            title=f"{name} social drop-in",
            description=f"Live demo event around {name}.",
            starts_at=now + timedelta(minutes=25 + (index * 17)),
            ends_at=None,
            cost_pence=_parse_cost_hint_to_pence(place.get("cost_hint")),
            tags=tags,
            tier=_to_demo_tier(category),
            venue=VenueSummary(
                name=name,
                lat=float(place_lat),
                lng=float(place_lng),
                address=str(place.get("address")) if place.get("address") else None,
            ),
        )
        scored.append((distance, event_summary))

    scored.sort(key=lambda item: item[0])
    if not scored:
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

    return EventsNearbyResponse(events=[event for _, event in scored[:limit]])


@router.get("/nearby", response_model=EventsNearbyResponse)
async def events_nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(default=5, gt=0, le=50),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EventsNearbyResponse:
    del current_user
    return await _build_events_nearby_response(
        session=session,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
    )


@router.get("/demo/nearby", response_model=EventsNearbyResponse)
async def demo_events_nearby(
    lat: float = Query(default=51.5274),
    lng: float = Query(default=-0.0777),
    radius_km: float = Query(default=8, gt=0, le=50),
    limit: int = Query(default=8, ge=1, le=50),
) -> EventsNearbyResponse:
    return _build_demo_seed_events(
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
    )


@router.get("/demo/attendees", response_model=EventAttendeesResponse)
async def demo_event_attendees(
    event_key: str = Query(..., min_length=1, max_length=255),
    title: str = Query(..., min_length=1, max_length=255),
    tags: str = Query(default=""),
    attendee_hint: int | None = Query(default=None, ge=1, le=80),
) -> EventAttendeesResponse:
    tag_list = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
    service = get_demo_social_graph_service()
    payload = service.build_attendees_for_event(
        event_key=event_key,
        event_title=title,
        event_tags=tag_list,
        attendee_hint=attendee_hint,
    )
    return EventAttendeesResponse(
        event_key=payload.event_key,
        event_title=payload.event_title,
        total_expected=payload.total_expected,
        solo_count=payload.solo_count,
        attendees=[
            EventAttendee(
                user_id=attendee.user_id,
                display_name=attendee.display_name,
                response=attendee.response,
                solo=attendee.solo,
                comfort_level=attendee.comfort_level,
                cohort=attendee.cohort,
                interests=attendee.interests,
            )
            for attendee in payload.attendees
        ],
    )
