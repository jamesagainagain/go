from __future__ import annotations

from datetime import UTC, datetime, timedelta


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return ensure_utc(value)

    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    parsed = datetime.fromisoformat(cleaned)
    return ensure_utc(parsed)


def is_within_next_hours(
    value: datetime,
    *,
    hours: int,
    now: datetime | None = None,
) -> bool:
    reference = ensure_utc(now or datetime.now(UTC))
    dt_value = ensure_utc(value)
    return reference <= dt_value <= reference + timedelta(hours=hours)


def minutes_until(value: datetime, *, now: datetime | None = None) -> int:
    reference = ensure_utc(now or datetime.now(UTC))
    delta = ensure_utc(value) - reference
    return int(delta.total_seconds() // 60)
