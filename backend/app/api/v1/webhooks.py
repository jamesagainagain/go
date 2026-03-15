from __future__ import annotations

from collections import deque
from json import JSONDecodeError
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.config import get_settings
from app.services.calendar_sync import (
    CalendarWebhookError,
    normalize_calendar_webhook_payload,
    verify_calendar_signature,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/calendar")
async def calendar_webhook(request: Request) -> dict[str, str]:
    raw_payload = await request.body()
    signature_header = request.headers.get("X-Calendar-Signature")
    webhook_secret = get_settings().calendar_webhook_secret
    if not webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook secret not configured.",
        )

    if not verify_calendar_signature(
        payload=raw_payload,
        signature_header=signature_header,
        secret=webhook_secret,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )

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

    events = getattr(request.app.state, "calendar_webhook_events", None)
    if not isinstance(events, deque):
        events = deque(maxlen=500)
    events.append(normalized)
    request.app.state.calendar_webhook_events = events
    return {"status": "ok"}
