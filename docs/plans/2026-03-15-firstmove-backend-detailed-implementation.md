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

## Completed Scope (Tasks 1-6)

- Task 1: branch bootstrap + pytest harness.
- Task 2: FastAPI app bootstrap, config, DB wiring, health/ready endpoints.
- Task 3: Supabase migration path with live upgrade/downgrade validation.
- Task 4: ORM domain model + UUID defaults + relational constraints.
- Task 5: API schemas and contract checks.
- Task 6: auth + user profile/location endpoints.

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

## Remaining Execution (Tasks 7-15)

Pending tasks remain the same in intent:

- Task 7: activation/events/push/webhook APIs.
- Task 8: LangGraph agent runtime path.
- Task 9: ingestion/enrichment/dedupe runtime.
- Task 10: notification/booking/calendar service abstractions.
- Task 11: Celery workers + schedules + reliability controls.
- Task 12: full regression and contract matrix.
- Task 13: production hardening and resilience.
- Task 14: end-to-end verification and release gate.
- Task 15: OpenClaw deferred integration seams.

Task 12 must preserve the already-fixed baseline regressions as mandatory checks.

## Verification Commands

Run from branch workspace:

- `cd /Users/james/go/backend && ruff check .`
- `cd /Users/james/go/backend && pytest -q`
- `cd /Users/james/go/backend && python3 -m scripts.seed_demo_social_proof --users 300 --seed 20260315`

