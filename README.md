# go!

An agentic system that competes with your sofa and wins.  
FirstMove is an activation engine that turns "I should go out" into concrete, nearby plans.

## What This Repo Contains

- `backend/` - FastAPI app, LangGraph agents, Celery workers, Alembic migrations
- `frontend/` - Next.js 14 app (PWA-style UX)
- `docs/` - API spec and architecture/planning docs
- `docker-compose.yml` - local infrastructure (API, worker, beat, PostGIS, Redis)

## API Contract (Source of Truth)

- OpenAPI spec: `docs/api-spec.yaml`
- Human-readable endpoint summary: `docs/API.md`

Frontend and backend should both stay aligned with this spec.

## Prerequisites

Install these first:

- Docker + Docker Compose
- Python 3.12+
- Node.js 20+ (recommended for Next.js 14)
- `make`

## 1) Environment Setup

From the repo root:

```bash
cp .env.example .env
```

Then edit `.env` and fill the values you need.  
For local development, these are the minimum useful fields:

- `DATABASE_URL` (already points to local Postgres in `.env.example`)
- `REDIS_URL` (already points to local Redis in `.env.example`)
- `SECRET_KEY` (change this)

Optional but commonly needed:

- `OPENAI_API_KEY` for agent features
- `MAPBOX_ACCESS_TOKEN` for map features
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for Supabase seeding script

### OpenClaw Profile Signals (Optional)

If you want OpenClaw-driven profile updates (activity-aware recommendation tuning), set:

```bash
OPENCLAW_ENABLED=true
OPENCLAW_ENDPOINT=https://api.openai.com/v1/chat/completions
OPENCLAW_API_TOKEN=<same value as OPENAI_API_KEY>
```

How this works:

- During activation checks, backend asks OpenClaw for near-term suggestions.
- Suggestion tags/categories are merged into inferred `user_preferences`.
- These inferred signals are low-weight and non-blocking (safe for demos).

For frontend local env, create `frontend/.env.local` and set:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=<your-mapbox-token>
NEXT_PUBLIC_VAPID_PUBLIC_KEY=<optional>
```

## 2) Start Backend Infrastructure

From repo root:

```bash
make up
```

This starts:

- API container on `http://localhost:8000`
- Celery worker
- Celery beat scheduler
- PostGIS database on `localhost:5432`
- Redis on `localhost:6379`

To stop everything:

```bash
make down
```

## 3) Run Database Migrations

Run once after first startup (and after schema changes):

```bash
cd backend
alembic upgrade head
```

## 4) Seed Demo Data

From repo root:

```bash
make seed
```

This runs `backend/scripts/seed_supabase_demo_places.py`.

## 5) Start Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`.

## 6) Verify Everything Is Working

Backend health checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected:

- `/health` returns `{"status":"ok"}`
- `/ready` shows database and redis checks

## 7) Run Tests

From repo root:

```bash
make test
```

Equivalent command:

```bash
cd backend && pytest tests/ -v
```

## Common Commands

From repo root:

- `make up` - start local services
- `make down` - stop local services
- `make seed` - seed demo places
- `make test` - run backend tests

Frontend:

- `npm run dev` - start dev server
- `npm run build` - production build
- `npm run lint` - lint frontend

## Troubleshooting

- API cannot connect to DB:
  - confirm `make up` is running
  - confirm `DATABASE_URL`/`SUPABASE_DB_URL` is set correctly in `.env`
- `/ready` reports redis false:
  - ensure Redis container is up (`make up`)
  - ensure `REDIS_URL` is valid
- Frontend cannot hit backend:
  - verify `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
  - verify API container is running on port `8000`

## Tech Stack

- Backend: Python 3.12, FastAPI, LangGraph, PostgreSQL + PostGIS, Redis, Celery, Alembic
- Frontend: Next.js 14, React 18, Tailwind, Mapbox
- Deployment targets: Railway / Fly.io (backend), Vercel (frontend)
