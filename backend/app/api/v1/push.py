from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import User
from app.services.notification import validate_push_subscription
from app.utils.security import get_current_user

router = APIRouter(prefix="/push", tags=["push"])


class PushSubscribeKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscribeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    endpoint: str
    expiration_time: float | None = Field(default=None, alias="expirationTime")
    keys: PushSubscribeKeys


@router.post("/subscribe")
async def subscribe_push(
    payload: PushSubscribeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    serialized_payload = payload.model_dump(by_alias=True)
    if not validate_push_subscription(serialized_payload):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subscription")

    current_user.push_subscription = serialized_payload
    await session.commit()
    return {"status": "ok"}
