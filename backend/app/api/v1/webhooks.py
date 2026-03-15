from __future__ import annotations

from json import JSONDecodeError
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.services.calendar_sync import CalendarWebhookError, normalize_calendar_webhook_payload

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/calendar")
async def calendar_webhook(request: Request) -> dict[str, str]:
    try:
        payload: Any = await request.json()
    except JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload.",
        ) from error

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload.",
        )

    try:
        normalized = normalize_calendar_webhook_payload(payload)
    except CalendarWebhookError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    events = getattr(request.app.state, "calendar_webhook_events", [])
    events.append(normalized)
    request.app.state.calendar_webhook_events = events
    return {"status": "ok"}
