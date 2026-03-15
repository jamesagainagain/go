from __future__ import annotations

import pytest

from app.models.enums import OpportunityTier
from app.services.booking import build_commitment_action
from app.services.calendar_sync import (
    CalendarWebhookError,
    DefaultCalendarProvider,
    normalize_calendar_webhook_payload,
)
from app.services.notification import NoopNotificationProvider, validate_push_subscription


@pytest.mark.services
def test_booking_commitment_action_mapping():
    structured = build_commitment_action(tier=OpportunityTier.STRUCTURED, source_url=None)
    recurring = build_commitment_action(tier=OpportunityTier.RECURRING_PATTERN, source_url=None)
    deep_link = build_commitment_action(
        tier=OpportunityTier.STRUCTURED,
        source_url="https://example.com/rsvp",
    )

    assert structured.type == "one_tap_rsvp"
    assert recurring.type == "internal_going"
    assert deep_link.type == "deep_link"
    assert deep_link.url == "https://example.com/rsvp"


@pytest.mark.services
@pytest.mark.asyncio
async def test_notification_provider_validates_subscription():
    provider = NoopNotificationProvider()
    valid_subscription = {
        "endpoint": "https://push.example.test/subscription/123",
        "keys": {"p256dh": "abc", "auth": "def"},
    }
    invalid_subscription = {"endpoint": "", "keys": {"p256dh": "abc"}}

    assert validate_push_subscription(valid_subscription) is True
    assert validate_push_subscription(invalid_subscription) is False

    delivered = await provider.send(subscription=valid_subscription, payload={"title": "hello"})
    failed = await provider.send(subscription=invalid_subscription, payload={"title": "hello"})
    assert delivered.delivered is True
    assert failed.delivered is False


@pytest.mark.services
def test_calendar_provider_normalization_and_validation():
    provider = DefaultCalendarProvider()
    normalized = provider.normalize({"resource_id": "calendar-42", "event_type": "updated"})

    assert normalized["resource_id"] == "calendar-42"
    assert normalized["event_type"] == "updated"
    assert "received_at" in normalized

    with pytest.raises(CalendarWebhookError):
        normalize_calendar_webhook_payload({"event_type": "updated"})
