from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.services.event_ingestion import EventSourceAdapter, RawEvent


class TicketmasterAdapter(EventSourceAdapter):
    name = "ticketmaster"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://app.ticketmaster.com/discovery/v2",
        country_code: str = "GB",
        timeout_seconds: float = 6.0,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._country_code = country_code
        self._timeout_seconds = timeout_seconds

    async def fetch_events(self, city: str, radius_km: float, hours_ahead: int) -> list[RawEvent]:
        payload = await self._fetch_payload(city=city, radius_km=radius_km, hours_ahead=hours_ahead)
        embedded = payload.get("_embedded", {})
        events = embedded.get("events") or []
        parsed_events: list[RawEvent] = []
        for event_payload in events:
            parsed = self._parse_event(event_payload)
            if parsed is not None:
                parsed_events.append(parsed)
        return parsed_events

    async def _fetch_payload(
        self,
        *,
        city: str,
        radius_km: float,
        hours_ahead: int,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (now + timedelta(hours=hours_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {
            "apikey": self._api_key,
            "city": city,
            "countryCode": self._country_code,
            "radius": radius_km,
            "unit": "km",
            "size": 200,
            "sort": "date,asc",
            "startDateTime": start,
            "endDateTime": end,
        }
        timeout = httpx.Timeout(self._timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{self._base_url}/events.json", params=params)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            return {}
        return payload

    def _parse_event(self, payload: Any) -> RawEvent | None:
        if not isinstance(payload, dict):
            return None

        title = _optional_text(payload.get("name"))
        if title is None:
            return None

        start_time = _extract_start_time(payload.get("dates"))
        if start_time is None:
            return None

        venue = _extract_primary_venue(payload)
        location_text = _build_location_text(venue)
        lat, lng = _extract_coordinates(venue)
        tags = _extract_tags(payload)
        source_url = _optional_text(payload.get("url"))
        description = _optional_text(payload.get("info")) or _optional_text(
            payload.get("pleaseNote")
        )
        return RawEvent(
            source_name=self.name,
            title=title,
            description=description,
            start_time=start_time,
            end_time=_extract_end_time(payload.get("dates")),
            location_text=location_text,
            lat=lat,
            lng=lng,
            source_url=source_url,
            cost_text=_extract_cost_text(payload),
            tags_raw=tags or None,
        )


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_start_time(dates_payload: Any) -> str | None:
    if not isinstance(dates_payload, dict):
        return None
    start_payload = dates_payload.get("start")
    if not isinstance(start_payload, dict):
        return None

    start_datetime = _optional_text(start_payload.get("dateTime"))
    if start_datetime:
        return start_datetime

    local_date = _optional_text(start_payload.get("localDate"))
    local_time = _optional_text(start_payload.get("localTime"))
    if local_date and local_time:
        return f"{local_date}T{local_time}"
    return local_date


def _extract_end_time(dates_payload: Any) -> str | None:
    if not isinstance(dates_payload, dict):
        return None
    end_payload = dates_payload.get("end")
    if not isinstance(end_payload, dict):
        return None

    end_datetime = _optional_text(end_payload.get("dateTime"))
    if end_datetime:
        return end_datetime

    local_date = _optional_text(end_payload.get("localDate"))
    local_time = _optional_text(end_payload.get("localTime"))
    if local_date and local_time:
        return f"{local_date}T{local_time}"
    return local_date


def _extract_primary_venue(payload: dict[str, Any]) -> dict[str, Any] | None:
    embedded = payload.get("_embedded")
    if not isinstance(embedded, dict):
        return None
    venues = embedded.get("venues")
    if not isinstance(venues, list) or not venues:
        return None
    venue = venues[0]
    if not isinstance(venue, dict):
        return None
    return venue


def _build_location_text(venue_payload: dict[str, Any] | None) -> str | None:
    if venue_payload is None:
        return None

    city_payload = venue_payload.get("city")
    address_payload = venue_payload.get("address")
    city = _optional_text(city_payload.get("name")) if isinstance(city_payload, dict) else None
    line = (
        _optional_text(address_payload.get("line1")) if isinstance(address_payload, dict) else None
    )
    parts = [
        _optional_text(venue_payload.get("name")),
        line,
        city,
        _optional_text(venue_payload.get("postalCode")),
    ]
    non_empty = [part for part in parts if part]
    if not non_empty:
        return None
    return ", ".join(non_empty)


def _extract_coordinates(venue_payload: dict[str, Any] | None) -> tuple[float | None, float | None]:
    if venue_payload is None:
        return None, None

    location = venue_payload.get("location")
    if not isinstance(location, dict):
        return None, None

    lat = _coerce_float(location.get("latitude"))
    lng = _coerce_float(location.get("longitude"))
    return lat, lng


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_cost_text(payload: dict[str, Any]) -> str | None:
    prices = payload.get("priceRanges")
    if not isinstance(prices, list) or not prices:
        return None

    first = prices[0]
    if not isinstance(first, dict):
        return None

    minimum = _coerce_float(first.get("min"))
    maximum = _coerce_float(first.get("max"))
    currency = _optional_text(first.get("currency")) or "GBP"
    if minimum is None and maximum is None:
        return None

    if currency == "GBP":
        if minimum is not None and maximum is not None and maximum != minimum:
            return f"£{minimum:.2f}-£{maximum:.2f}"
        if minimum is not None:
            return f"£{minimum:.2f}"
        return f"£{maximum:.2f}"

    if minimum is not None and maximum is not None and maximum != minimum:
        return f"{minimum:.2f}-{maximum:.2f} {currency}"
    if minimum is not None:
        return f"{minimum:.2f} {currency}"
    return f"{maximum:.2f} {currency}"


def _extract_tags(payload: dict[str, Any]) -> list[str]:
    classifications = payload.get("classifications")
    if not isinstance(classifications, list):
        return []

    tags: list[str] = []
    for item in classifications:
        if not isinstance(item, dict):
            continue
        for key in ("segment", "genre", "subGenre", "type", "subType"):
            section = item.get(key)
            if not isinstance(section, dict):
                continue
            name = _optional_text(section.get("name"))
            if not name:
                continue
            normalized = name.lower()
            if normalized not in tags:
                tags.append(normalized)
    return tags[:6]
