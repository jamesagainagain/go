from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.database import get_session_factory
from app.models import User
from app.tasks import (
    TaskLockBackendUnavailableError,
    acquire_task_lock,
    celery_app,
    release_task_lock,
)


async def _load_candidate_user_ids(limit: int) -> list[str]:
    cutoff = datetime.now(UTC) - timedelta(days=7)
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(User.id)
            .where(User.created_at >= cutoff)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
    return [str(user_id) for user_id in result.scalars().all()]


async def _run_activation_checks_async(limit: int) -> dict[str, object]:
    user_ids = await _load_candidate_user_ids(limit)
    enqueued = len(user_ids)
    return {
        "status": "ok",
        "users_considered": len(user_ids),
        "enqueued": enqueued,
    }


@celery_app.task(
    bind=True,
    name="app.tasks.run_activations.run_activation_checks",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_activation_checks(
    self,  # noqa: ANN001
    limit: int = 200,
) -> dict[str, object]:
    del self
    lock_key = "task-lock:run-activations"
    lock_acquired = False
    try:
        lock_acquired = acquire_task_lock(lock_key, ttl_seconds=600)
    except TaskLockBackendUnavailableError as error:
        raise RuntimeError("task_lock_backend_unavailable") from error

    if not lock_acquired:
        return {"status": "skipped", "reason": "lock_active"}

    try:
        return asyncio.run(_run_activation_checks_async(limit=limit))
    finally:
        if lock_acquired:
            try:
                release_task_lock(lock_key)
            except TaskLockBackendUnavailableError:
                pass
