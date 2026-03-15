from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import quote_plus

import httpx

from app.config import get_settings

STATIC_LOCATION_LOOKUP = {
    "shoreditch": (51.5247, -0.0794),
    "bloomsbury": (51.5235, -0.1259),
    "victoria park": (51.5360, -0.0382),
    "camden": (51.5390, -0.1426),
}


@dataclass(slots=True)
class GeocodeResult:
    lat: float
    lng: float
    source: str


class Geocoder(Protocol):
    async def geocode(self, location_text: str) -> GeocodeResult | None:
        ...


class GeocodingService:
    def __init__(self, *, mapbox_token: str | None = None, timeout_seconds: float = 2.0) -> None:
        settings = get_settings()
        self._mapbox_token = (
            mapbox_token if mapbox_token is not None else settings.mapbox_access_token
        )
        self._timeout_seconds = timeout_seconds

    async def geocode(self, location_text: str) -> GeocodeResult | None:
        query = location_text.strip()
        if not query:
            return None

        static_match = self._match_static_location(query)
        if static_match is not None:
            return static_match

        if not self._mapbox_token:
            return None
        return await self._lookup_mapbox(query)

    def _match_static_location(self, location_text: str) -> GeocodeResult | None:
        lowered = location_text.lower()
        for key, coordinates in STATIC_LOCATION_LOOKUP.items():
            if key in lowered:
                return GeocodeResult(lat=coordinates[0], lng=coordinates[1], source="static")
        return None

    async def _lookup_mapbox(self, query: str) -> GeocodeResult | None:
        url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
        request_url = url.format(query=quote_plus(query))
        params = {"access_token": self._mapbox_token, "limit": 1}
        timeout = httpx.Timeout(self._timeout_seconds)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(request_url, params=params)
                response.raise_for_status()
        except (httpx.HTTPError, ValueError):
            return None

        payload = response.json()
        features = payload.get("features") or []
        if not features:
            return None
        center = features[0].get("center")
        if not isinstance(center, list) or len(center) != 2:
            return None
        lng, lat = center
        return GeocodeResult(lat=float(lat), lng=float(lng), source="mapbox")
