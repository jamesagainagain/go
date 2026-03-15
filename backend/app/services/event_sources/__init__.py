from __future__ import annotations

from app.services.event_ingestion import EventSourceAdapter
from app.services.event_sources.openclaw_adapter import OpenClawEventSourceAdapter
from app.services.event_sources.places_catalog_adapter import PlacesCatalogAdapter
from app.services.openclaw import build_openclaw_provider


def build_default_event_source_adapters(
    *,
    include_places_catalog: bool,
    openclaw_enabled: bool,
    openclaw_endpoint: str | None,
    openclaw_api_token: str | None,
    openclaw_timeout_seconds: float,
    openclaw_model: str = "gpt-4o-mini",
) -> list[EventSourceAdapter]:
    adapters: list[EventSourceAdapter] = []
    if include_places_catalog:
        adapters.append(PlacesCatalogAdapter())
    adapters.append(
        OpenClawEventSourceAdapter(
            provider=build_openclaw_provider(
                enabled=openclaw_enabled,
                endpoint=openclaw_endpoint,
                api_token=openclaw_api_token,
                timeout_seconds=openclaw_timeout_seconds,
                model=openclaw_model,
            )
        )
    )
    return adapters


__all__ = [
    "build_default_event_source_adapters",
    "PlacesCatalogAdapter",
    "OpenClawEventSourceAdapter",
]
