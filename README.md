# go! 

An agentic system that competes with your sofa - and wins. Activation engine from screen to street.

## API Specification

**Unified API spec:** `docs/api-spec.yaml` (OpenAPI 3.0)

Frontend and backend must both implement against this spec. See `docs/API.md` for a quick reference.

## Structure

- `backend/` - FastAPI, LangGraph agents, Celery tasks
- `frontend/` - Next.js 14 PWA
- `data/` - Seed data and scrapers

## Setup

1. Copy `.env.example` to `.env` and fill in your values
2. `make install` - create backend venv and install Python deps (first time only)
3. `make up` - start Docker services (Postgres, Redis)
4. `make seed` - load demo data (requires Supabase; see `.env.example` for `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY`)
5. `make test` - run backend tests

## Tech Stack

- **Backend:** Python 3.12, FastAPI, LangGraph, PostgreSQL + PostGIS, Redis, Celery
- **Frontend:** Next.js 14, Tailwind, Mapbox
- **Deploy:** Railway / Fly.io, Vercel
