from __future__ import annotations

from functools import lru_cache

from celery import Celery
from redis import Redis

from app.config import get_settings

TASK_MODULES = [
    "app.tasks.ingest_events",
    "app.tasks.run_activations",
    "app.tasks.cleanup",
]


def create_celery_app() -> Celery:
    settings = get_settings()
    celery = Celery(
        "firstmove",
        broker=settings.redis_url,
        backend=settings.redis_url,
        include=TASK_MODULES,
    )
    celery.conf.update(
        timezone="UTC",
        enable_utc=True,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_soft_time_limit=45,
        task_time_limit=60,
        beat_schedule={
            "ingest-events-hourly": {
                "task": "app.tasks.ingest_events.run_event_ingestion",
                "schedule": 60 * 60,
                "args": ("london", 5.0, 48),
            },
            "run-activations-periodic": {
                "task": "app.tasks.run_activations.run_activation_checks",
                "schedule": settings.activation_check_interval_minutes * 60,
                "kwargs": {"limit": 200},
            },
            "cleanup-expired-opportunities": {
                "task": "app.tasks.cleanup.cleanup_expired_records",
                "schedule": 30 * 60,
            },
        },
    )
    return celery


@lru_cache
def get_celery_app() -> Celery:
    return create_celery_app()


def acquire_task_lock(key: str, *, ttl_seconds: int = 900) -> bool:
    client: Redis | None = None
    try:
        client = Redis.from_url(get_settings().redis_url, decode_responses=True)
        return bool(client.set(name=key, value="1", nx=True, ex=ttl_seconds))
    except Exception:
        return True
    finally:
        if client is not None:
            client.close()


def release_task_lock(key: str) -> None:
    client: Redis | None = None
    try:
        client = Redis.from_url(get_settings().redis_url, decode_responses=True)
        client.delete(key)
    except Exception:
        return
    finally:
        if client is not None:
            client.close()


celery_app = get_celery_app()

# Ensure tasks are imported so decorators register routes at app startup.
from app.tasks import cleanup, ingest_events, run_activations  # noqa: E402, F401
