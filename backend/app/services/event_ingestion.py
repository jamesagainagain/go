from __future__ import annotations

import asyncio
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from difflib import SequenceMatcher
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, OpportunityTier, Venue
from app.services.geocoding import Geocoder, GeocodeResult, GeocodingService
from app.utils.geo import haversine_km
from app.utils.llm import estimate_solo_friendly_score, extract_tags_from_text
from app.utils.time_helpers import parse_datetime


class RawEvent(BaseModel):
    source_name: str
    title: str
    description: str | None = None
    start_time: datetime | str
    end_time: datetime | str | None = None
    location_text: str | None = None
    lat: float | None = None
    lng: float | None = None
    source_url: str | None = None
    cost_text: str | None = None
    tags_raw: list[str] | None = None


class NormalizedEvent(BaseModel):
    source: str
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime | None = None
    location_text: str | None = None
    lat: float | None = None
    lng: float | None = None
    source_url: str | None = None
    cost_pence: int = 0
    tags: list[str] = Field(default_factory=list)
    solo_friendly_score: float = 0.5
    dedupe_key: str


class EventSourceAdapter(Protocol):
    name: str

    async def fetch_events(self, city: str, radius_km: float, hours_ahead: int) -> list[RawEvent]:
        ...


@dataclass(slots=True)
class IngestionResult:
    events: list[NormalizedEvent]
    source_errors: dict[str, str]


class EventIngestionService:
    def __init__(
        self,
        *,
        adapters: Iterable[EventSourceAdapter] | None = None,
        geocoder: Geocoder | None = None,
        request_timeout_seconds: float = 5.0,
        max_retries: int = 2,
    ) -> None:
        self._adapters: dict[str, EventSourceAdapter] = {}
        for adapter in adapters or []:
            self._adapters[adapter.name] = adapter
        self._geocoder = geocoder or GeocodingService()
        self._request_timeout_seconds = request_timeout_seconds
        self._max_retries = max_retries

    def register_provider(self, name: str, adapter: EventSourceAdapter) -> None:
        self._adapters[name] = adapter

    def available_providers(self) -> list[str]:
        return sorted(self._adapters.keys())

    async def fetch_normalized_events(
        self,
        *,
        city: str,
        radius_km: float,
        hours_ahead: int,
    ) -> IngestionResult:
        raw_events: list[RawEvent] = []
        source_errors: dict[str, str] = {}
        for name, adapter in self._adapters.items():
            try:
                fetched = await self._fetch_with_retry(
                    adapter=adapter,
                    city=city,
                    radius_km=radius_km,
                    hours_ahead=hours_ahead,
                )
            except Exception as error:  # noqa: BLE001
                source_errors[name] = str(error)
                continue
            raw_events.extend(fetched)

        normalized = []
        for event in raw_events:
            try:
                normalized_event = await self.normalize_event(event)
            except Exception as error:  # noqa: BLE001
                source_errors[f"normalize:{event.source_name.lower()}"] = str(error)
                continue
            if normalized_event:
                normalized.append(normalized_event)
        deduped = self.dedupe_events(normalized)
        return IngestionResult(events=deduped, source_errors=source_errors)

    async def _fetch_with_retry(
        self,
        *,
        adapter: EventSourceAdapter,
        city: str,
        radius_km: float,
        hours_ahead: int,
    ) -> list[RawEvent]:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                return await asyncio.wait_for(
                    adapter.fetch_events(city=city, radius_km=radius_km, hours_ahead=hours_ahead),
                    timeout=self._request_timeout_seconds,
                )
            except Exception as error:  # noqa: BLE001
                last_error = error
                if attempt + 1 >= self._max_retries:
                    break
        if last_error is None:
            raise RuntimeError(f"Adapter {adapter.name} failed without an error.")
        raise last_error

    async def normalize_event(self, raw_event: RawEvent) -> NormalizedEvent | None:
        starts_at = parse_datetime(raw_event.start_time)
        if starts_at is None:
            return None
        ends_at = parse_datetime(raw_event.end_time)

        geocode_result: GeocodeResult | None = None
        lat = raw_event.lat
        lng = raw_event.lng
        if (lat is None or lng is None) and raw_event.location_text:
            geocode_result = await self._geocoder.geocode(raw_event.location_text)
            if geocode_result is not None:
                lat = geocode_result.lat
                lng = geocode_result.lng

        description = (raw_event.description or "").strip()
        combined_text = f"{raw_event.title} {description}".strip()
        tags = self._normalize_tags(raw_event.tags_raw, combined_text)
        solo_friendly_score = estimate_solo_friendly_score(combined_text)
        cost_pence = parse_cost_to_pence(raw_event.cost_text)
        dedupe_key = self._dedupe_key(
            title=raw_event.title,
            starts_at=starts_at,
            lat=lat,
            lng=lng,
        )
        return NormalizedEvent(
            source=raw_event.source_name.strip().lower(),
            title=raw_event.title.strip(),
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            location_text=raw_event.location_text,
            lat=lat,
            lng=lng,
            source_url=raw_event.source_url,
            cost_pence=cost_pence,
            tags=tags,
            solo_friendly_score=solo_friendly_score,
            dedupe_key=dedupe_key,
        )

    def dedupe_events(self, events: list[NormalizedEvent]) -> list[NormalizedEvent]:
        deduped: list[NormalizedEvent] = []
        for candidate in sorted(events, key=lambda item: item.starts_at):
            merged = False
            for index, existing in enumerate(deduped):
                if self._is_duplicate(existing, candidate):
                    deduped[index] = self._choose_richer(existing, candidate)
                    merged = True
                    break
            if not merged:
                deduped.append(candidate)
        return deduped

    async def upsert_events(
        self,
        *,
        session: AsyncSession,
        events: list[NormalizedEvent],
    ) -> tuple[int, int]:
        inserted = 0
        updated = 0

        for event in events:
            existing = await self._find_existing_event(session=session, event=event)
            if existing is not None:
                existing.description = event.description
                existing.ends_at = event.ends_at
                existing.cost_pence = event.cost_pence
                existing.tags = event.tags
                existing.solo_friendly_score = event.solo_friendly_score
                updated += 1
                continue

            venue_id = await self._resolve_venue_id(session=session, event=event)
            session.add(
                Event(
                    venue_id=venue_id,
                    title=event.title,
                    description=event.description,
                    starts_at=event.starts_at,
                    ends_at=event.ends_at,
                    tier=OpportunityTier.STRUCTURED,
                    source=event.source,
                    source_url=event.source_url,
                    cost_pence=event.cost_pence,
                    tags=event.tags,
                    attendee_count_estimate=None,
                    solo_friendly_score=event.solo_friendly_score,
                )
            )
            inserted += 1

        await session.commit()
        return inserted, updated

    async def _find_existing_event(
        self,
        *,
        session: AsyncSession,
        event: NormalizedEvent,
    ) -> Event | None:
        if event.source_url:
            result = await session.execute(
                select(Event).where(
                    and_(Event.source == event.source, Event.source_url == event.source_url)
                )
            )
            existing = result.scalar_one_or_none()
            if existing is not None:
                return existing

        result = await session.execute(
            select(Event).where(
                and_(
                    Event.source == event.source,
                    Event.title == event.title,
                    Event.starts_at == event.starts_at,
                )
            )
        )
        return result.scalar_one_or_none()

    async def _resolve_venue_id(
        self,
        *,
        session: AsyncSession,
        event: NormalizedEvent,
    ) -> UUID | None:
        if not event.location_text:
            return None

        venue_name = event.location_text[:255]
        result = await session.execute(select(Venue).where(Venue.name == venue_name))
        venue = result.scalar_one_or_none()
        if venue is None:
            venue = Venue(name=venue_name, address=event.location_text, source_url=event.source_url)
            session.add(venue)
            await session.flush()
        return venue.id

    def _normalize_tags(self, tags_raw: list[str] | None, text: str) -> list[str]:
        cleaned = [tag.strip().lower() for tag in (tags_raw or []) if tag.strip()]
        llm_tags = extract_tags_from_text(text)
        merged = cleaned + [tag for tag in llm_tags if tag not in cleaned]
        return merged[:6]

    def _dedupe_key(
        self,
        *,
        title: str,
        starts_at: datetime,
        lat: float | None,
        lng: float | None,
    ) -> str:
        rounded_lat = "none" if lat is None else f"{lat:.3f}"
        rounded_lng = "none" if lng is None else f"{lng:.3f}"
        normalized_title = re.sub(r"\s+", " ", title.strip().lower())
        start_bucket = starts_at.astimezone(UTC).strftime("%Y%m%d%H")
        return f"{normalized_title}|{start_bucket}|{rounded_lat}|{rounded_lng}"

    def _is_duplicate(self, left: NormalizedEvent, right: NormalizedEvent) -> bool:
        title_similarity = SequenceMatcher(a=left.title.lower(), b=right.title.lower()).ratio()
        time_diff_minutes = abs((left.starts_at - right.starts_at).total_seconds()) / 60

        if title_similarity < 0.8 or time_diff_minutes > 30:
            return False

        if left.lat is None or left.lng is None or right.lat is None or right.lng is None:
            return True
        distance = haversine_km(left.lat, left.lng, right.lat, right.lng)
        return distance <= 0.2

    def _choose_richer(self, left: NormalizedEvent, right: NormalizedEvent) -> NormalizedEvent:
        left_richness = _event_richness(left)
        right_richness = _event_richness(right)
        return left if left_richness >= right_richness else right


def parse_cost_to_pence(cost_text: str | None) -> int:
    if not cost_text:
        return 0

    normalized = cost_text.strip().lower()
    if normalized in {"free", "0", "£0", "0 gbp", "free entry"}:
        return 0

    amount_match = re.search(r"(\d+(?:\.\d+)?)", normalized)
    if amount_match is None:
        return 0
    amount = float(amount_match.group(1))

    if "p" in normalized and "£" not in normalized and "gbp" not in normalized:
        return int(amount)
    return int(round(amount * 100))


def _event_richness(event: NormalizedEvent) -> int:
    score = 0
    if event.description:
        score += 1
    if event.source_url:
        score += 1
    if event.lat is not None and event.lng is not None:
        score += 1
    if event.tags:
        score += 1
    if event.ends_at is not None:
        score += 1
    return score
