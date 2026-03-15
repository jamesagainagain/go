from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol


class CalendarWebhookError(ValueError):
    pass


class CalendarProvider(Protocol):
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...


def normalize_calendar_webhook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    resource_id = payload.get("resource_id") or payload.get("resourceId")
    event_type = payload.get("event_type") or payload.get("eventType") or "updated"

    if not resource_id:
        raise CalendarWebhookError("Missing resource_id.")

    return {
        "resource_id": str(resource_id),
        "event_type": str(event_type),
        "received_at": datetime.now(UTC).isoformat(),
        "raw": payload,
    }


class DefaultCalendarProvider:
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return normalize_calendar_webhook_payload(payload)
