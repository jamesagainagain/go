from __future__ import annotations

import pytest

import app.tasks as tasks_module
from app.tasks import (
    TaskLockBackendUnavailableError,
    cleanup,
    get_celery_app,
    ingest_events,
    run_activations,
)


@pytest.mark.tasks
def test_celery_app_registers_tasks_and_schedule():
    celery_app = get_celery_app()
    assert "app.tasks.ingest_events.run_event_ingestion" in celery_app.tasks
    assert "app.tasks.run_activations.run_activation_checks" in celery_app.tasks
    assert "app.tasks.cleanup.cleanup_expired_records" in celery_app.tasks

    schedule = celery_app.conf.beat_schedule
    assert "ingest-events-hourly" in schedule
    assert "run-activations-periodic" in schedule
    assert "cleanup-expired-opportunities" in schedule


@pytest.mark.tasks
def test_ingest_events_task_returns_structured_result(monkeypatch: pytest.MonkeyPatch):
    async def fake_ingestion(city: str, radius_km: float, hours_ahead: int) -> dict[str, object]:
        assert city == "london"
        assert radius_km == 5.0
        assert hours_ahead == 12
        return {
            "status": "ok",
            "fetched": 2,
            "inserted": 1,
            "updated": 1,
            "source_errors": {},
        }

    monkeypatch.setattr(ingest_events, "acquire_task_lock", lambda key, ttl_seconds=900: True)
    monkeypatch.setattr(ingest_events, "release_task_lock", lambda key: None)
    monkeypatch.setattr(ingest_events, "_run_event_ingestion_async", fake_ingestion)

    result = ingest_events.run_event_ingestion(city="london", radius_km=5.0, hours_ahead=12)
    assert result["status"] == "ok"
    assert result["inserted"] == 1
    assert result["updated"] == 1


@pytest.mark.tasks
def test_run_activations_task_skips_when_locked(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(run_activations, "acquire_task_lock", lambda key, ttl_seconds=600: False)
    monkeypatch.setattr(run_activations, "release_task_lock", lambda key: None)

    result = run_activations.run_activation_checks(limit=50)
    assert result == {"status": "skipped", "reason": "lock_active"}


@pytest.mark.tasks
def test_run_activations_task_returns_enqueue_counts(monkeypatch: pytest.MonkeyPatch):
    async def fake_run(limit: int) -> dict[str, object]:
        assert limit == 25
        return {"status": "ok", "users_considered": 10, "enqueued": 10}

    monkeypatch.setattr(run_activations, "acquire_task_lock", lambda key, ttl_seconds=600: True)
    monkeypatch.setattr(run_activations, "release_task_lock", lambda key: None)
    monkeypatch.setattr(run_activations, "_run_activation_checks_async", fake_run)

    result = run_activations.run_activation_checks(limit=25)
    assert result["status"] == "ok"
    assert result["enqueued"] == 10


@pytest.mark.tasks
def test_cleanup_task_reports_deleted_counts(monkeypatch: pytest.MonkeyPatch):
    async def fake_cleanup() -> tuple[int, int]:
        return 2, 3

    monkeypatch.setattr(cleanup, "acquire_task_lock", lambda key, ttl_seconds=300: True)
    monkeypatch.setattr(cleanup, "release_task_lock", lambda key: None)
    monkeypatch.setattr(cleanup, "_cleanup_async", fake_cleanup)

    result = cleanup.cleanup_expired_records()
    assert result["status"] == "ok"
    assert result["deleted_activations"] == 2
    assert result["deleted_opportunities"] == 3


@pytest.mark.tasks
def test_task_lock_fails_safe_when_redis_unavailable(monkeypatch: pytest.MonkeyPatch):
    def raise_on_connect(*args, **kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(tasks_module.Redis, "from_url", raise_on_connect)
    with pytest.raises(TaskLockBackendUnavailableError):
        tasks_module.acquire_task_lock("task-lock:test", ttl_seconds=60)


@pytest.mark.tasks
def test_event_ingestion_service_registers_local_places_from_settings(
    monkeypatch: pytest.MonkeyPatch,
):
    class FakeSettings:
        enable_places_catalog_ingestion = True
        openclaw_enabled = False
        openclaw_endpoint = None
        openclaw_api_token = None
        openclaw_timeout_seconds = 4.0

    monkeypatch.setattr(ingest_events, "get_settings", lambda: FakeSettings())
    ingest_events.set_event_ingestion_service(None)  # type: ignore[arg-type]

    service = ingest_events.get_event_ingestion_service()
    assert "local_places" in service.available_providers()
    ingest_events.set_event_ingestion_service(None)  # type: ignore[arg-type]


@pytest.mark.tasks
def test_event_ingestion_service_can_disable_local_places(
    monkeypatch: pytest.MonkeyPatch,
):
    class FakeSettings:
        enable_places_catalog_ingestion = False
        openclaw_enabled = False
        openclaw_endpoint = None
        openclaw_api_token = None
        openclaw_timeout_seconds = 4.0

    monkeypatch.setattr(ingest_events, "get_settings", lambda: FakeSettings())
    ingest_events.set_event_ingestion_service(None)  # type: ignore[arg-type]

    service = ingest_events.get_event_ingestion_service()
    assert "local_places" not in service.available_providers()
    ingest_events.set_event_ingestion_service(None)  # type: ignore[arg-type]
