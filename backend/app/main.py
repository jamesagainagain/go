from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.v1 import api_router
from app.config import get_settings
from app.database import check_database_connection


async def _build_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.redis = await _build_redis_client()
    try:
        yield
    finally:
        await app.state.redis.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="FirstMove Backend",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", tags=["system"])
    async def ready() -> dict[str, object]:
        db_ok = await check_database_connection()
        redis_ok = False
        try:
            redis_ok = await app.state.redis.ping()
        except Exception:
            redis_ok = False
        return {
            "status": "ready" if db_ok and redis_ok else "degraded",
            "checks": {"database": db_ok, "redis": redis_ok},
        }

    return app


app = create_app()
