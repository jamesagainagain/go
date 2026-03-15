from fastapi import APIRouter

from app.api.v1.activations import router as activations_router
from app.api.v1.auth import router as auth_router
from app.api.v1.events import router as events_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.push import router as push_router
from app.api.v1.users import router as users_router
from app.api.v1.webhooks import router as webhooks_router

api_router = APIRouter()


@api_router.get("/ping", tags=["system"])
async def ping() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(activations_router)
api_router.include_router(feedback_router)
api_router.include_router(events_router)
api_router.include_router(push_router)
api_router.include_router(webhooks_router)
