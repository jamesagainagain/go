from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

from app.database import get_session_factory
from app.models import Activation, Opportunity
from app.tasks import acquire_task_lock, celery_app, release_task_lock


async def _cleanup_async() -> tuple[int, int]:
    now = datetime.now(UTC)
    stale_activation_cutoff = now - timedelta(days=30)
    expired_opportunity_cutoff = now - timedelta(hours=6)

    session_factory = get_session_factory()
    async with session_factory() as session:
        activation_result = await session.execute(
            delete(Activation)
            .where(
                Activation.response.is_(None),
                Activation.shown_at < stale_activation_cutoff,
            )
            .returning(Activation.id)
        )
        opportunity_result = await session.execute(
            delete(Opportunity)
            .where(Opportunity.expires_at < expired_opportunity_cutoff)
            .returning(Opportunity.id)
        )
        await session.commit()

    deleted_activations = len(list(activation_result.scalars().all()))
    deleted_opportunities = len(list(opportunity_result.scalars().all()))
    return deleted_activations, deleted_opportunities


@celery_app.task(
    bind=True,
    name="app.tasks.cleanup.cleanup_expired_records",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def cleanup_expired_records(self) -> dict[str, object]:  # noqa: ANN001
    del self
    lock_key = "task-lock:cleanup"
    if not acquire_task_lock(lock_key, ttl_seconds=300):
        return {"status": "skipped", "reason": "lock_active"}

    try:
        deleted_activations, deleted_opportunities = asyncio.run(_cleanup_async())
        return {
            "status": "ok",
            "deleted_activations": deleted_activations,
            "deleted_opportunities": deleted_opportunities,
        }
    finally:
        release_task_lock(lock_key)
