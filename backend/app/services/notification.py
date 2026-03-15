from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class PushDeliveryResult:
    delivered: bool
    reason: str | None = None


class NotificationProvider(Protocol):
    async def send(
        self,
        *,
        subscription: dict[str, Any],
        payload: dict[str, Any],
    ) -> PushDeliveryResult:
        ...


def validate_push_subscription(payload: dict[str, Any]) -> bool:
    keys = payload.get("keys")
    if not isinstance(keys, dict):
        return False
    return bool(payload.get("endpoint") and keys.get("p256dh") and keys.get("auth"))


async def send_push_notification(
    *,
    subscription: dict[str, Any],
    payload: dict[str, Any],
) -> PushDeliveryResult:
    del payload
    if not validate_push_subscription(subscription):
        return PushDeliveryResult(delivered=False, reason="Invalid subscription payload.")
    return PushDeliveryResult(delivered=True)


class NoopNotificationProvider:
    async def send(
        self,
        *,
        subscription: dict[str, Any],
        payload: dict[str, Any],
    ) -> PushDeliveryResult:
        return await send_push_notification(subscription=subscription, payload=payload)
