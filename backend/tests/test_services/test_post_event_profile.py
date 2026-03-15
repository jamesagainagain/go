from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models import Activation, ActivationResponse, Opportunity, OpportunityTier
from app.services.post_event_profile import _build_feedback_review, _preference_weight_delta


def _activation_for_review(*, response: ActivationResponse) -> Activation:
    opportunity = Opportunity(
        title="Evening canal walk",
        body="Solo-friendly community walk for all levels.",
        tier=OpportunityTier.SOLO_NUDGE,
        expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
    return Activation(opportunity=opportunity, response=response)


@pytest.mark.services
def test_build_feedback_review_positive_follow_through() -> None:
    activation = _activation_for_review(response=ActivationResponse.ACCEPTED)

    review = _build_feedback_review(
        activation,
        attended=True,
        rating=5,
        feedback_text="Loved it, very friendly and easy to join solo.",
    )

    assert review.stage_direction == "up"
    assert review.comfort_direction == "towards_solo"
    assert review.tags


@pytest.mark.services
def test_build_feedback_review_negative_experience() -> None:
    activation = _activation_for_review(response=ActivationResponse.ACCEPTED)

    review = _build_feedback_review(
        activation,
        attended=False,
        rating=2,
        feedback_text="Too much friction and not a good fit.",
    )

    assert review.stage_direction == "down"
    assert review.comfort_direction == "towards_support"
    assert review.tags


@pytest.mark.services
def test_preference_weight_delta_reflects_outcome() -> None:
    assert _preference_weight_delta(attended=True, rating=5) > 0
    assert _preference_weight_delta(attended=False, rating=1) < 0
