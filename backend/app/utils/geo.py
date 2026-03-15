from __future__ import annotations

from math import atan2, cos, degrees, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def is_within_radius(
    *,
    origin_lat: float,
    origin_lng: float,
    target_lat: float,
    target_lng: float,
    radius_km: float,
) -> bool:
    return haversine_km(origin_lat, origin_lng, target_lat, target_lng) <= radius_km


def bounding_box(lat: float, lng: float, radius_km: float) -> tuple[float, float, float, float]:
    lat_delta = degrees(radius_km / EARTH_RADIUS_KM)
    lng_delta = degrees(radius_km / EARTH_RADIUS_KM / max(cos(radians(lat)), 1e-6))
    return (
        lat - lat_delta,
        lat + lat_delta,
        lng - lng_delta,
        lng + lng_delta,
    )


def midpoint(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    if not points:
        return None

    x = 0.0
    y = 0.0
    z = 0.0
    for lat, lng in points:
        lat_rad = radians(lat)
        lng_rad = radians(lng)
        x += cos(lat_rad) * cos(lng_rad)
        y += cos(lat_rad) * sin(lng_rad)
        z += sin(lat_rad)

    total = float(len(points))
    x /= total
    y /= total
    z /= total
    lng_rad = atan2(y, x)
    hyp = sqrt(x * x + y * y)
    lat_rad = atan2(z, hyp)
    return degrees(lat_rad), degrees(lng_rad)
