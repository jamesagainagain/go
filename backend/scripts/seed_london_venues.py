from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.database import get_session_factory
from app.models import Venue
from app.services.venue_resolver import DEFAULT_VENUE_CATALOG_PATH, LondonVenueCatalog


def _build_point(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


async def seed_london_venues(catalog_path: Path) -> dict[str, int]:
    catalog = LondonVenueCatalog(catalog_path=catalog_path)
    inserted = 0
    updated = 0

    session_factory = get_session_factory()
    async with session_factory() as session:
        for entry in catalog.entries:
            result = await session.execute(select(Venue).where(Venue.name == entry.name))
            venue = result.scalar_one_or_none()
            point = _build_point(entry.lat, entry.lng)

            if venue is None:
                session.add(
                    Venue(
                        name=entry.name,
                        address=entry.address,
                        location=point,
                        venue_type=entry.venue_type,
                        capacity_estimate=entry.capacity_estimate,
                        vibe_tags=list(entry.vibe_tags) if entry.vibe_tags else None,
                        source_url=entry.source_url,
                    )
                )
                inserted += 1
                continue

            venue.address = entry.address or venue.address
            venue.location = point
            venue.venue_type = entry.venue_type or venue.venue_type
            venue.capacity_estimate = (
                entry.capacity_estimate
                if entry.capacity_estimate is not None
                else venue.capacity_estimate
            )
            if entry.vibe_tags:
                venue.vibe_tags = list(entry.vibe_tags)
            if entry.source_url:
                venue.source_url = entry.source_url
            updated += 1

        await session.commit()

    return {
        "catalog_entries": len(catalog.entries),
        "inserted": inserted,
        "updated": updated,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed curated London venues into the DB.")
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_VENUE_CATALOG_PATH),
        help="Path to london_venues.json catalog",
    )
    args = parser.parse_args()
    result = asyncio.run(seed_london_venues(Path(args.catalog)))
    print(result)


if __name__ == "__main__":
    main()
