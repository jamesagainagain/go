from __future__ import annotations

import pytest

from app.services.demo_social_graph import DemoSocialGraphService


@pytest.mark.services
def test_demo_social_graph_builds_attendees_from_event_tags():
    service = DemoSocialGraphService()

    payload = service.build_attendees_for_event(
        event_key="event-abc-123",
        event_title="After-work life drawing session",
        event_tags=["art", "community"],
        attendee_hint=18,
    )

    assert payload.total_expected >= 6
    assert payload.solo_count >= 1
    assert len(payload.attendees) >= 10
    assert any("art" in attendee.interests for attendee in payload.attendees)


@pytest.mark.services
def test_demo_social_graph_is_stable_for_same_event_input():
    service = DemoSocialGraphService()

    first = service.build_attendees_for_event(
        event_key="event-stable-1",
        event_title="Canal walk and coffee social",
        event_tags=["outdoors", "community", "food"],
        attendee_hint=16,
    )
    second = service.build_attendees_for_event(
        event_key="event-stable-1",
        event_title="Canal walk and coffee social",
        event_tags=["outdoors", "community", "food"],
        attendee_hint=16,
    )

    assert first.total_expected == second.total_expected
    assert first.solo_count == second.solo_count
    assert [attendee.user_id for attendee in first.attendees[:5]] == [
        attendee.user_id for attendee in second.attendees[:5]
    ]
