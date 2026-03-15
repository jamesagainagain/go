from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "seeds" / "london_local_places.json"

TIER_BY_CATEGORY = {
    "museum": "structured",
    "gallery": "structured",
    "restaurant": "micro_coordination",
    "cafe": "micro_coordination",
    "food_market": "micro_coordination",
    "park": "solo_nudge",
}

WALK_MINUTES_BY_CATEGORY = {
    "museum": 14,
    "gallery": 12,
    "restaurant": 10,
    "cafe": 8,
    "food_market": 10,
    "park": 7,
}


@dataclass(slots=True)
class SeedStats:
    venues_inserted: int = 0
    venues_updated: int = 0
    events_inserted: int = 0
    events_updated: int = 0
    opportunities_inserted: int = 0
    opportunities_updated: int = 0


def _load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), value.strip())


def _load_default_env_files() -> None:
    candidates: list[Path] = [REPO_ROOT / ".env"]
    for parent in REPO_ROOT.parents:
        candidates.append(parent / ".env")
        if parent.name == ".worktrees":
            candidates.append(parent.parent / ".env")
            break

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        _load_dotenv(candidate)


def _to_slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return cleaned.strip("-")


def _parse_cost_to_pence(cost_hint: str | None) -> int:
    if not cost_hint:
        return 0
    normalized = cost_hint.strip().lower()
    if normalized in {"free", "£0", "0", "0 gbp"}:
        return 0
    match = re.search(r"(\d+(?:\.\d+)?)", normalized)
    if match is None:
        return 0
    amount = float(match.group(1))
    return int(round(amount * 100))


def _build_headers(service_key: str) -> dict[str, str]:
    return {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _coerce_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _tier_for_category(category: str) -> str:
    return TIER_BY_CATEGORY.get(category, "micro_coordination")


def _walk_minutes_for_category(category: str) -> int:
    return WALK_MINUTES_BY_CATEGORY.get(category, 10)


def _load_catalog(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Catalog payload must be a list.")

    cleaned: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = _coerce_text(item.get("name"))
        if not name:
            continue
        try:
            lat = float(item.get("lat"))
            lng = float(item.get("lng"))
        except (TypeError, ValueError):
            continue
        if lat < -90 or lat > 90 or lng < -180 or lng > 180:
            continue
        cleaned.append(item)
    return cleaned


def _json_or_raise(response: httpx.Response) -> Any:
    response.raise_for_status()
    return response.json()


def _get_single_row(
    client: httpx.Client,
    url: str,
    headers: dict[str, str],
    table: str,
    query_params: dict[str, str],
) -> dict[str, Any] | None:
    params = {"select": "*", "limit": "1"}
    params.update(query_params)
    response = client.get(f"{url}/rest/v1/{table}", headers=headers, params=params)
    rows = _json_or_raise(response)
    if isinstance(rows, list) and rows:
        return rows[0]
    return None


def _upsert_venue(
    client: httpx.Client,
    *,
    url: str,
    headers: dict[str, str],
    place: dict[str, Any],
) -> tuple[str, bool]:
    name = str(place["name"]).strip()
    existing = _get_single_row(
        client,
        url,
        headers,
        "venues",
        {"name": f"eq.{name}"},
    )
    payload = {
        "name": name,
        "address": _coerce_text(place.get("address")),
        "location": f"POINT({float(place['lng'])} {float(place['lat'])})",
        "venue_type": _coerce_text(place.get("category")),
        "vibe_tags": [
            str(tag).strip().lower()
            for tag in place.get("tags", [])
            if str(tag).strip()
        ],
        "source_url": _coerce_text(place.get("source_url")),
    }

    if existing is None:
        response = client.post(f"{url}/rest/v1/venues", headers=headers, json=payload)
        inserted_rows = _json_or_raise(response)
        return str(inserted_rows[0]["id"]), True

    venue_id = str(existing["id"])
    response = client.patch(
        f"{url}/rest/v1/venues",
        headers=headers,
        params={"id": f"eq.{venue_id}"},
        json=payload,
    )
    _json_or_raise(response)
    return venue_id, False


def _upsert_event(
    client: httpx.Client,
    *,
    url: str,
    headers: dict[str, str],
    place: dict[str, Any],
    venue_id: str,
    starts_at: datetime,
) -> tuple[str, bool]:
    place_name = str(place["name"]).strip()
    slug = _to_slug(place_name)
    source_url = f"local://place/{slug}"
    category = str(place.get("category", "")).strip().lower()
    title = f"Local plan at {place_name}"

    existing = _get_single_row(
        client,
        url,
        headers,
        "events",
        {
            "source": "eq.local_places",
            "source_url": f"eq.{source_url}",
        },
    )
    payload = {
        "venue_id": venue_id,
        "title": title,
        "description": (
            f"Drop-in {category.replace('_', ' ')} option at {place_name} for live demo flows."
        ),
        "starts_at": starts_at.isoformat(),
        "ends_at": (starts_at + timedelta(hours=2)).isoformat(),
        "tier": _tier_for_category(category),
        "source": "local_places",
        "source_url": source_url,
        "cost_pence": _parse_cost_to_pence(_coerce_text(place.get("cost_hint"))),
        "tags": _build_event_tags(place, category),
        "attendee_count_estimate": 8,
        "solo_friendly_score": 0.72,
    }

    if existing is None:
        response = client.post(f"{url}/rest/v1/events", headers=headers, json=payload)
        inserted_rows = _json_or_raise(response)
        return str(inserted_rows[0]["id"]), True

    event_id = str(existing["id"])
    response = client.patch(
        f"{url}/rest/v1/events",
        headers=headers,
        params={"id": f"eq.{event_id}"},
        json=payload,
    )
    _json_or_raise(response)
    return event_id, False


def _build_event_tags(place: dict[str, Any], category: str) -> list[str]:
    tags = [category, "local_places"]
    for value in place.get("tags", []):
        tag = str(value).strip().lower()
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:6]


def _upsert_opportunity(
    client: httpx.Client,
    *,
    url: str,
    headers: dict[str, str],
    place: dict[str, Any],
    event_id: str,
    starts_at: datetime,
) -> bool:
    place_name = str(place["name"]).strip()
    category = str(place.get("category", "")).strip().lower()
    tier = _tier_for_category(category)
    title = f"Go now: {place_name}"

    existing = _get_single_row(
        client,
        url,
        headers,
        "opportunities",
        {"event_id": f"eq.{event_id}", "title": f"eq.{title}"},
    )
    walk_minutes = _walk_minutes_for_category(category)
    payload = {
        "event_id": event_id,
        "tier": tier,
        "title": title,
        "body": (
            f"Real local option from curated London places: {place_name}. "
            "Use this for live demo recommendation flows."
        ),
        "walk_minutes": walk_minutes,
        "travel_description": f"{walk_minutes} min walk",
        "social_proof_text": "2 others going solo",
        "expires_at": (starts_at + timedelta(hours=1)).isoformat(),
        "location": f"POINT({float(place['lng'])} {float(place['lat'])})",
    }

    if existing is None:
        response = client.post(f"{url}/rest/v1/opportunities", headers=headers, json=payload)
        _json_or_raise(response)
        return True

    opportunity_id = str(existing["id"])
    response = client.patch(
        f"{url}/rest/v1/opportunities",
        headers=headers,
        params={"id": f"eq.{opportunity_id}"},
        json=payload,
    )
    _json_or_raise(response)
    return False


def seed_demo_places(
    *,
    supabase_url: str,
    service_key: str,
    catalog_path: Path,
    hours_ahead: int,
) -> SeedStats:
    places = _load_catalog(catalog_path)
    stats = SeedStats()
    now = datetime.now(UTC).replace(second=0, microsecond=0)
    window_hours = max(1, min(hours_ahead, 24))

    headers = _build_headers(service_key)
    with httpx.Client(timeout=30.0) as client:
        for index, place in enumerate(places):
            starts_at = now + timedelta(hours=1 + (index % window_hours))

            venue_id, venue_inserted = _upsert_venue(
                client,
                url=supabase_url,
                headers=headers,
                place=place,
            )
            if venue_inserted:
                stats.venues_inserted += 1
            else:
                stats.venues_updated += 1

            event_id, event_inserted = _upsert_event(
                client,
                url=supabase_url,
                headers=headers,
                place=place,
                venue_id=venue_id,
                starts_at=starts_at,
            )
            if event_inserted:
                stats.events_inserted += 1
            else:
                stats.events_updated += 1

            opp_inserted = _upsert_opportunity(
                client,
                url=supabase_url,
                headers=headers,
                place=place,
                event_id=event_id,
                starts_at=starts_at,
            )
            if opp_inserted:
                stats.opportunities_inserted += 1
            else:
                stats.opportunities_updated += 1

    return stats


def main() -> None:
    _load_default_env_files()

    parser = argparse.ArgumentParser(
        description="Seed demo museum/restaurant/place data into Supabase via REST API."
    )
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG_PATH),
        help="Path to local places JSON catalog.",
    )
    parser.add_argument(
        "--hours-ahead",
        type=int,
        default=48,
        help="How far ahead synthetic start windows should be generated.",
    )
    parser.add_argument(
        "--supabase-url",
        default=None,
        help="Supabase project URL (falls back to SUPABASE_URL env).",
    )
    parser.add_argument(
        "--service-key",
        default=None,
        help="Supabase service role/secret key (falls back to env).",
    )
    args = parser.parse_args()

    supabase_url = args.supabase_url or os.environ.get("SUPABASE_URL")
    service_key = args.service_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get(
        "SUPABASE_SECRET_KEY"
    )
    if not supabase_url or not service_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY/SUPABASE_SECRET_KEY are required."
        )

    stats = seed_demo_places(
        supabase_url=supabase_url,
        service_key=service_key,
        catalog_path=Path(args.catalog),
        hours_ahead=args.hours_ahead,
    )
    print(
        {
            "venues_inserted": stats.venues_inserted,
            "venues_updated": stats.venues_updated,
            "events_inserted": stats.events_inserted,
            "events_updated": stats.events_updated,
            "opportunities_inserted": stats.opportunities_inserted,
            "opportunities_updated": stats.opportunities_updated,
        }
    )


if __name__ == "__main__":
    main()
