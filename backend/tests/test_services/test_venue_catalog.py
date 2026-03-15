from __future__ import annotations

import pytest

from app.services.geocoding import GeocodingService
from app.services.venue_resolver import LondonVenueCatalog


@pytest.mark.services
def test_london_venue_catalog_has_detailed_entries():
    catalog = LondonVenueCatalog()
    assert len(catalog.entries) >= 25
    names = {entry.name for entry in catalog.entries}
    assert {"Barbican Centre", "Southbank Centre", "Roundhouse"}.issubset(names)


@pytest.mark.services
def test_london_venue_catalog_matches_aliases():
    catalog = LondonVenueCatalog()
    match = catalog.find_match("Life Drawing Session at Barbican Arts Centre")
    assert match is not None
    assert match.entry.name == "Barbican Centre"


@pytest.mark.services
@pytest.mark.asyncio
async def test_geocoder_prefers_catalog_coordinates():
    catalog = LondonVenueCatalog()
    service = GeocodingService(mapbox_token=None, venue_catalog=catalog)

    result = await service.geocode("Southbank Centre, London")
    assert result is not None
    assert result.source == "catalog"
    assert result.lat == pytest.approx(51.5068, abs=0.001)
    assert result.lng == pytest.approx(-0.1167, abs=0.001)
