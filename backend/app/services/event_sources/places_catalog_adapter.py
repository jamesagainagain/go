from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.services.event_ingestion import EventSourceAdapter, RawEvent

REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_PLACES_CATALOG_PATH = REPO_ROOT / "data" / "seeds" / "london_local_places.json"

LOCAL_PLACE_CATEGORY_TAGS: dict[str, tuple[str, str]] = {
    "museum": ("culture", "structured"),
    "gallery": ("art", "structured"),
    "restaurant": ("food", "micro_coordination"),
    "cafe": ("coffee", "micro_coordination"),
    "park": ("outdoors", "solo_nudge"),
    "food_market": ("food", "micro_coordination"),
}


class PlacesCatalogAdapter(EventSourceAdapter):
    name = "local_places"

    def __init__(
        self,
        *,
        catalog_path: Path | None = None,
        max_places: int = 120,
    ) -> None:
        self._catalog_path = catalog_path or DEFAULT_PLACES_CATALOG_PATH
        self._max_places = max_places

    async def fetch_events(self, city: str, radius_km: float, hours_ahead: int) -> list[RawEvent]:
        del radius_km
        if city.strip().lower() != "london":
            return []

        places = self._load_places()
        if not places:
            return []

        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        window_hours = max(1, min(hours_ahead, 12))
        events: list[RawEvent] = []

        for index, place in enumerate(places[: self._max_places]):
            start_time = now + timedelta(hours=1 + (index % window_hours))
            category = str(place.get("category", "")).strip().lower()
            category_tag, tier_tag = LOCAL_PLACE_CATEGORY_TAGS.get(
                category,
                ("community", "micro_coordination"),
            )

            title = _build_place_title(
                place_name=str(place["name"]),
                category=category,
            )
            description = _build_place_description(
                place_name=str(place["name"]),
                category=category,
                borough=str(place.get("borough", "")).strip() or None,
            )
            raw_tags = [category, category_tag, tier_tag]
            raw_tags.extend(_coerce_tags(place.get("tags")))
            unique_tags = _dedupe_tags(raw_tags)

            location_text = _build_location_text(
                place_name=str(place["name"]),
                address=str(place.get("address", "")).strip() or None,
            )
            events.append(
                RawEvent(
                    source_name=self.name,
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=2),
                    location_text=location_text,
                    lat=float(place["lat"]),
                    lng=float(place["lng"]),
                    source_url=_optional_text(place.get("source_url")),
                    cost_text=_optional_text(place.get("cost_hint")),
                    tags_raw=unique_tags,
                )
            )

        return events

    def _load_places(self) -> list[dict[str, Any]]:
        if not self._catalog_path.exists():
            return []

        try:
            payload = json.loads(self._catalog_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(payload, list):
            return []

        places: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            if not _is_valid_place_record(item):
                continue
            places.append(item)
        return places


def _is_valid_place_record(payload: dict[str, Any]) -> bool:
    name = _optional_text(payload.get("name"))
    if not name:
        return False

    try:
        lat = float(payload.get("lat"))
        lng = float(payload.get("lng"))
    except (TypeError, ValueError):
        return False
    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
        return False
    return True


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _build_location_text(place_name: str, address: str | None) -> str:
    if address:
        return f"{place_name}, {address}"
    return place_name


def _build_place_title(place_name: str, category: str) -> str:
    normalized = category.lower()
    if normalized in {"museum", "gallery"}:
        return f"Cultural drop-in at {place_name}"
    if normalized in {"restaurant", "food_market"}:
        return f"Try a food stop at {place_name}"
    if normalized == "park":
        return f"Reset walk at {place_name}"
    if normalized == "cafe":
        return f"Coffee social at {place_name}"
    return f"Local place activity at {place_name}"


def _build_place_description(place_name: str, category: str, borough: str | None) -> str:
    place_type = category.replace("_", " ").strip() or "local spot"
    zone = f" in {borough}" if borough else ""
    return (
        f"Low-friction {place_type} option at {place_name}{zone}. "
        "Designed for fast, realistic local demo opportunities."
    )


def _coerce_tags(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    tags: list[str] = []
    for item in value:
        text = _optional_text(item)
        if text:
            tags.append(text.lower())
    return tags


def _dedupe_tags(tags: list[str]) -> list[str]:
    unique: list[str] = []
    for tag in tags:
        normalized = tag.strip().lower()
        if not normalized:
            continue
        if normalized not in unique:
            unique.append(normalized)
    return unique[:6]
