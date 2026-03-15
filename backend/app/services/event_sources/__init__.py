from __future__ import annotations

from app.services.event_ingestion import EventSourceAdapter
from app.services.event_sources.ticketmaster_adapter import TicketmasterAdapter


def build_default_event_source_adapters(
    *,
    ticketmaster_api_key: str | None,
) -> list[EventSourceAdapter]:
    adapters: list[EventSourceAdapter] = []
    if ticketmaster_api_key:
        adapters.append(TicketmasterAdapter(api_key=ticketmaster_api_key))
    return adapters


__all__ = ["build_default_event_source_adapters", "TicketmasterAdapter"]
