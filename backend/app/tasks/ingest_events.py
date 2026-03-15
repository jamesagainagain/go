from __future__ import annotations

import asyncio

from app.database import get_session_factory
from app.services.event_ingestion import EventIngestionService
from app.tasks import acquire_task_lock, celery_app, release_task_lock

_event_ingestion_service: EventIngestionService | None = None


def get_event_ingestion_service() -> EventIngestionService:
    global _event_ingestion_service
    if _event_ingestion_service is None:
        _event_ingestion_service = EventIngestionService()
    return _event_ingestion_service


def set_event_ingestion_service(service: EventIngestionService) -> None:
    global _event_ingestion_service
    _event_ingestion_service = service


async def _run_event_ingestion_async(
    city: str,
    radius_km: float,
    hours_ahead: int,
) -> dict[str, object]:
    service = get_event_ingestion_service()
    result = await service.fetch_normalized_events(
        city=city,
        radius_km=radius_km,
        hours_ahead=hours_ahead,
    )

    inserted = 0
    updated = 0
    if result.events:
        session_factory = get_session_factory()
        async with session_factory() as session:
            inserted, updated = await service.upsert_events(session=session, events=result.events)

    return {
        "status": "ok",
        "fetched": len(result.events),
        "inserted": inserted,
        "updated": updated,
        "source_errors": result.source_errors,
    }


@celery_app.task(
    bind=True,
    name="app.tasks.ingest_events.run_event_ingestion",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_event_ingestion(
    self,  # noqa: ANN001
    city: str = "london",
    radius_km: float = 5.0,
    hours_ahead: int = 48,
) -> dict[str, object]:
    del self
    lock_key = "task-lock:ingest-events"
    if not acquire_task_lock(lock_key, ttl_seconds=900):
        return {"status": "skipped", "reason": "lock_active"}

    try:
        return asyncio.run(
            _run_event_ingestion_async(city=city, radius_km=radius_km, hours_ahead=hours_ahead)
        )
    finally:
        release_task_lock(lock_key)
