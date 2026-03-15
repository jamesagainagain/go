from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_VENUE_CATALOG_PATH = REPO_ROOT / "data" / "seeds" / "london_venues.json"


def _normalize_text(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\s]+", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


@dataclass(frozen=True, slots=True)
class VenueCatalogEntry:
    name: str
    aliases: tuple[str, ...]
    address: str | None
    postcode: str | None
    borough: str | None
    lat: float
    lng: float
    venue_type: str | None
    capacity_estimate: int | None
    vibe_tags: tuple[str, ...]
    source_url: str | None
    confidence: str | None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> VenueCatalogEntry | None:
        name = str(payload.get("name", "")).strip()
        if not name:
            return None

        lat = payload.get("lat")
        lng = payload.get("lng")
        if not isinstance(lat, (float, int)) or not isinstance(lng, (float, int)):
            return None
        if lat < -90 or lat > 90 or lng < -180 or lng > 180:
            return None

        aliases_payload = payload.get("aliases") or []
        aliases: list[str] = []
        for item in aliases_payload:
            alias = str(item).strip()
            if alias:
                aliases.append(alias)

        tags_payload = payload.get("vibe_tags") or []
        vibe_tags: list[str] = []
        for item in tags_payload:
            tag = str(item).strip().lower()
            if tag:
                vibe_tags.append(tag)

        capacity_value = payload.get("capacity_estimate")
        capacity_estimate = int(capacity_value) if isinstance(capacity_value, int) else None

        return cls(
            name=name,
            aliases=tuple(aliases),
            address=_optional_text(payload.get("address")),
            postcode=_optional_text(payload.get("postcode")),
            borough=_optional_text(payload.get("borough")),
            lat=float(lat),
            lng=float(lng),
            venue_type=_optional_text(payload.get("venue_type")),
            capacity_estimate=capacity_estimate,
            vibe_tags=tuple(vibe_tags),
            source_url=_optional_text(payload.get("source_url")),
            confidence=_optional_text(payload.get("confidence")),
        )


@dataclass(frozen=True, slots=True)
class VenueMatch:
    entry: VenueCatalogEntry
    score: float
    alias: str


class LondonVenueCatalog:
    def __init__(self, *, catalog_path: Path | None = None) -> None:
        self._catalog_path = catalog_path or DEFAULT_VENUE_CATALOG_PATH
        self._entries = self._load_entries()
        self._alias_index = self._build_alias_index(self._entries)

    @property
    def entries(self) -> tuple[VenueCatalogEntry, ...]:
        return self._entries

    def find_match(self, location_text: str, *, min_score: float = 0.82) -> VenueMatch | None:
        normalized_query = _normalize_text(location_text)
        if not normalized_query:
            return None

        direct_hit = self._alias_index.get(normalized_query)
        if direct_hit is not None:
            return VenueMatch(entry=direct_hit, score=1.0, alias=normalized_query)

        best_entry: VenueCatalogEntry | None = None
        best_alias = ""
        best_score = 0.0
        for alias, entry in self._alias_index.items():
            if alias in normalized_query:
                score = 0.97
            elif normalized_query in alias:
                score = 0.9
            else:
                score = SequenceMatcher(a=normalized_query, b=alias).ratio()

            if score > best_score:
                best_entry = entry
                best_alias = alias
                best_score = score

        if best_entry is None or best_score < min_score:
            return None
        return VenueMatch(entry=best_entry, score=best_score, alias=best_alias)

    def _load_entries(self) -> tuple[VenueCatalogEntry, ...]:
        if not self._catalog_path.exists():
            return ()

        try:
            payload = json.loads(self._catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ()
        if not isinstance(payload, list):
            return ()

        entries: list[VenueCatalogEntry] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            entry = VenueCatalogEntry.from_payload(item)
            if entry is not None:
                entries.append(entry)
        return tuple(entries)

    def _build_alias_index(
        self,
        entries: tuple[VenueCatalogEntry, ...],
    ) -> dict[str, VenueCatalogEntry]:
        index: dict[str, VenueCatalogEntry] = {}
        for entry in entries:
            for alias in _collect_aliases(entry):
                normalized_alias = _normalize_text(alias)
                if not normalized_alias:
                    continue
                index.setdefault(normalized_alias, entry)
        return index


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _collect_aliases(entry: VenueCatalogEntry) -> tuple[str, ...]:
    aliases = [entry.name]
    aliases.extend(entry.aliases)
    return tuple(aliases)


@lru_cache(maxsize=1)
def get_london_venue_catalog(catalog_path: str | None = None) -> LondonVenueCatalog:
    path = Path(catalog_path) if catalog_path else DEFAULT_VENUE_CATALOG_PATH
    return LondonVenueCatalog(catalog_path=path)
