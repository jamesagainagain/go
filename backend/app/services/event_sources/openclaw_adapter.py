from __future__ import annotations

from app.services.event_ingestion import EventSourceAdapter, RawEvent
from app.services.openclaw import OpenClawProvider


class OpenClawEventSourceAdapter(EventSourceAdapter):
    name = "openclaw"

    def __init__(self, *, provider: OpenClawProvider) -> None:
        self._provider = provider

    async def fetch_events(self, city: str, radius_km: float, hours_ahead: int) -> list[RawEvent]:
        del radius_km
        suggestions = await self._provider.fetch_suggestions(city=city, hours_ahead=hours_ahead)
        events: list[RawEvent] = []
        for suggestion in suggestions:
            events.append(
                RawEvent(
                    source_name=self.name,
                    title=suggestion.title,
                    description=suggestion.description,
                    start_time=suggestion.starts_at,
                    location_text=suggestion.location_text,
                    lat=suggestion.lat,
                    lng=suggestion.lng,
                    source_url=suggestion.source_url,
                    cost_text=suggestion.cost_hint,
                    tags_raw=suggestion.tags,
                )
            )
        return events
