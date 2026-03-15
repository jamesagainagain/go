# FirstMove Backend Detailed Implementation Plan (Execution Ledger)

## Critical References

- `/Users/james/go/GoOverviewMotivation.pdf`
- `/Users/james/go/GoSystemArchitecture.pdf`
- `/Users/james/go/docs/API.md`
- `/Users/james/go/docs/api-spec.yaml`

This branch-level plan file tracks what has been completed, what was fixed immediately,
and what remains. It exists to prevent confusion about whether current bugs are deferred
to later tasks.

## Architecture Alignment Check

Current implementation remains aligned with the architecture documents:

- FastAPI contract-first backend over `/api/v1`.
- Async SQLAlchemy + Alembic migrations against Supabase/Postgres.
- Redis-backed runtime state and readiness probes.
- Clear path to LangGraph agents + Celery orchestration in later tasks.
- Social proof modeled as first-class data for activation cards.

No core repository layout changes were introduced.

## Completed Scope (Tasks 1-11)

- Task 1: branch bootstrap + pytest harness.
- Task 2: FastAPI app bootstrap, config, DB wiring, health/ready endpoints.
- Task 3: Supabase migration path with live upgrade/downgrade validation.
- Task 4: ORM domain model + UUID defaults + relational constraints.
- Task 5: API schemas and contract checks.
- Task 6: auth + user profile/location endpoints.
- Task 7: activation/events/push/webhook APIs with integration tests.
- Task 8: agent pipeline modules (context/discovery/social-proof/commitment/momentum)
  and orchestrator tests.
- Task 9: ingestion normalization, geocoding fallback, dedupe logic, provider registry,
  and service tests.
- Task 10: booking/notification/calendar provider abstractions + service tests.
- Task 11: Celery app, beat schedules, lock-based reliability guards, and task tests.

## Current Batch Delivered (Tasks 7-9)

- New `/api/v1` routes now active:
  - `/activations/check`, `/activations/current`, `/activations/{id}/respond`,
    `/activations/{id}/feedback`, `/activations/history`
  - `/events/nearby`
  - `/push/subscribe`
  - `/webhooks/calendar`
- Added API integration coverage for activation/events/push/webhook flows:
  `/Users/james/go/backend/tests/test_api/test_activation_endpoints.py`
- Implemented agent runtime components:
  - `app/agents/types.py`
  - `app/agents/context_agent.py`
  - `app/agents/discovery_agent.py`
  - `app/agents/social_proof_agent.py`
  - `app/agents/commitment_agent.py`
  - `app/agents/momentum_agent.py`
  - `app/agents/orchestrator.py`
- Added agent branch tests:
  `/Users/james/go/backend/tests/test_agents/test_orchestrator.py`
- Implemented ingestion services and utilities:
  - `app/services/event_ingestion.py`
  - `app/services/geocoding.py`
  - `app/utils/geo.py`
  - `app/utils/time_helpers.py`
  - `app/utils/llm.py`
- Added ingestion tests:
  `/Users/james/go/backend/tests/test_services/test_event_ingestion.py`
- Added delivery abstraction tests:
  `/Users/james/go/backend/tests/test_services/test_delivery_services.py`
- Added task runtime tests:
  `/Users/james/go/backend/tests/test_tasks/test_celery_tasks.py`

## Baseline Bugfixes Implemented Now (Not Deferred)

The following were fixed immediately and are now protected by tests.

1. Password contract parity (fixed now)

- `RegisterRequest.password` is required, matching `api-spec.yaml`.
- OpenAPI schema now marks `password` as required.
- Regression tests added for schema + OpenAPI parity.

2. Duplicate preference categories causing 500s (fixed now)

- Preference categories are normalized (`strip().lower()`).
- Duplicate categories are rejected in request validation before DB write.
- Endpoints now return clean 422 responses for duplicate category payloads.
- DB integrity fallback handling added to prevent uncaught 500s.

3. Async DB engine lifecycle across app restarts (fixed now)

- Engine/session globals are disposed/reset during app lifespan shutdown.
- Sequential `TestClient` lifecycle regression test added to prevent
  cross-event-loop failures.

4. Coverage gaps for above regressions (fixed now)

- Added tests for required password behavior.
- Added tests for duplicate preference rejection (register + update).
- Added lifecycle integration test for repeated app start/stop contexts.

These are considered complete fixes and should not be postponed to Task 12.
Task 12 must keep them as regression gates.

## Demo Social-Proof Dataset (Generated)

Requirement: demo must show believable "who is going" behavior.

Implemented now:

- Deterministic synthetic data generator:
  `/Users/james/go/backend/scripts/seed_demo_social_proof.py`
- Generated artifacts:
  - `/Users/james/go/data/seeds/synthetic_users.json`
  - `/Users/james/go/data/seeds/synthetic_user_activity.json`
- Validation tests:
  `/Users/james/go/backend/tests/test_services/test_demo_seed_data.py`

Dataset contract:

- Exactly 300 synthetic users.
- Diverse traits across:
  - comfort levels: `solo_ok`, `prefer_others`, `need_familiar`
  - preference vectors (weighted categories)
  - willingness radius and activation stage
  - location zones/cohorts
- Includes social-proof attendance snapshots for demo opportunities.
- Includes walkthrough-ready scenario coverage:
  - `post_work_drift`
  - `weekend_morning_void`
  - `cancelled_plan_gap`
- Deterministic by seed for stable demo reruns.

## Demo Walkthrough Alignment

The synthetic dataset is structured for a clear demo flow:

1. Pick a seeded user persona from the walkthrough set.
2. Trigger activation check flow.
3. Show one opportunity card with social-proof fields:
   `total_expected`, `solo_count`, familiar-cluster context.
4. Respond to activation and observe deterministic updates.

This directly supports the motivation doc goal: reducing activation friction from
screen-time to real-world action with visible social confidence cues.

## Tasks 12-15 Completion (Fast Demo Path)

All remaining tasks are now executed to a demo-ready standard in this worktree:

- Task 12 (regression + contract matrix) - completed:
  - Full backend matrix rerun with current adapters and API surface.
  - Regression coverage includes local-place ingestion, event filtering, and payload mapping.
  - Current verification status: `ruff check` clean, `pytest -q` passing (67 tests).

- Task 13 (hardening + resilience) - completed:
  - Data ingestion path is resilient to partial failures and malformed records.
  - Supabase REST seeding is idempotent (re-runs update existing rows, no duplicate growth).
  - Seeding CLI now supports explicit `--supabase-url` and `--service-key` for stable runtime.

- Task 14 (E2E verification + release gate) - completed:
  - End-to-end smoke path validated: catalog -> ingestion -> Supabase rows.
  - Re-seeding pass confirmed update behavior:
    - venues: 20 updated
    - events: 20 updated
    - opportunities: 20 updated
  - Local quality gate passed on latest code state.

- Task 15 (OpenClaw deferred framework) - completed as framework-only seam:
  - Added OpenClaw provider abstraction and adapter wiring.
  - Added config flags (`OPENCLAW_*`) and default non-blocking behavior.
  - Integration is intentionally non-critical and disabled by default.
  - No hard dependency is introduced for demo runtime.

## London Real Event + Venue Data Track (Added Before Execution)

You requested London-first realism for places/events with custom geolocation control.
This is now an explicit execution track mapped to remaining tasks:

- Strategy: **hybrid**
  - local London place ingestion (museums, restaurants, cafes, galleries, parks)
  - curated London venue catalog with canonical lat/lng overrides
  - deterministic fallback dataset for demo continuity

Ticketmaster note:

- Ticketmaster ingestion is intentionally removed from the active demo path.
- Demo ingestion uses local place catalogs and Supabase REST seeding so it works
  even when direct event-provider keys or direct Postgres connectivity are unstable.

- Task 12 extension (test/contract matrix):
  - add detailed `data/seeds/london_venues.json` catalog coverage + schema tests
  - add source-adapter tests for local place catalog parsing
  - add regression tests proving `/events/nearby` returns real ingested London events

- Task 13 extension (hardening):
  - add venue resolver priority: curated catalog > provider coordinates > geocoder fallback
  - add London-boundary coordinate guardrails and observability for provider failures

- Task 14 extension (release gate):
  - run E2E smoke proving local-place ingestion populates venue-aware payloads
  - validate fallback behavior when provider/network is unavailable

- Task 15 implementation note:
  - OpenClaw remains deferred in behavior but now has framework scaffolding in place.

Sync note:

- Implementation is currently in `/Users/james/go/.worktrees/demo-places`.
- Sync into `/Users/james/go` can be done as a final stage merge/cherry-pick step.

## Deferred Bug Backlog Status

The previously deferred backlog from the full-codebase scan has now been implemented
and covered with tests:

1. Event geo-filter correctness gap (`/events/nearby`) - **fixed now**

- `radius_km` is now enforced via PostGIS `ST_DWithin`.
- Added regression test coverage in `tests/test_api/test_events_nearby_logic.py`.

2. Venue coordinate mapping gap in API payloads - **fixed now**

- Event and activation responses now map venue lat/lng from PostGIS location data.
- Added regression test coverage in:
  - `tests/test_api/test_events_nearby_logic.py`
  - `tests/test_api/test_activation_mapping_logic.py`

3. Webhook runtime hardening gap - **fixed now**

- Added HMAC signature verification (`X-Calendar-Signature`) for calendar webhooks.
- Added bounded in-memory webhook queue (`deque(maxlen=500)`) to prevent unbounded growth.
- Added tests for valid/invalid signature and malformed JSON handling.

4. Task lock behavior under Redis failures — **fixed now**

- Lock acquisition/release now raises a dedicated backend-unavailable error.
- Celery tasks surface this error for retry handling instead of silent starvation.
- Added task test coverage for Redis-unavailable lock path.

5. Ingestion error observability granularity - **fixed now**

- Normalization failures now produce per-record error entries
  (`normalize:<source>:<index>`) including title and parse reason.
- Venue point writes now guard against invalid lat/lng ranges before PostGIS insert.
- Added regression test for invalid-record skip + granular error reporting.

## Verification Commands

Run from branch workspace:

- `cd /Users/james/go/.worktrees/demo-places/backend && ruff check app tests scripts`
- `cd /Users/james/go/.worktrees/demo-places/backend && pytest -q`
- `cd /Users/james/go/.worktrees/demo-places/backend && python3 -m scripts.seed_demo_social_proof --users 300 --seed 20260315`
- `cd /Users/james/go/.worktrees/demo-places/backend && python3 -m scripts.seed_london_venues`
- `cd /Users/james/go/.worktrees/demo-places/backend && python3 -m scripts.seed_supabase_demo_places --supabase-url \"$SUPABASE_URL\" --service-key \"$SUPABASE_SERVICE_ROLE_KEY\"`

