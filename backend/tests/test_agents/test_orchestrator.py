from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.agents.orchestrator import run_activation_pipeline
from app.agents.types import ActivationCandidate, ActivationState
from app.models.enums import ActivationStage, ComfortLevel, OpportunityTier


def _candidate(
    candidate_id: str,
    *,
    title: str,
    starts_in_minutes: int,
    base_time: datetime,
    tags: list[str],
    distance_km: float,
    tier: OpportunityTier = OpportunityTier.STRUCTURED,
) -> ActivationCandidate:
    return ActivationCandidate(
        candidate_id=candidate_id,
        title=title,
        body=f"{title} details",
        tier=tier,
        starts_at=base_time + timedelta(minutes=starts_in_minutes),
        walk_minutes=10,
        travel_description="10 min walk",
        distance_km=distance_km,
        tags=tags,
    )


@pytest.mark.agents
def test_pipeline_early_exit_when_context_gate_fails():
    now = datetime(2026, 3, 15, 3, 0, tzinfo=UTC)
    state = ActivationState(
        user_id=uuid4(),
        current_time=now,
        last_nudge_at=now - timedelta(minutes=30),
        user_preferences=["art"],
        candidates=[
            _candidate(
                "candidate-1",
                title="Early event",
                starts_in_minutes=45,
                base_time=now,
                tags=["art"],
                distance_km=1.0,
            )
        ],
    )

    result = run_activation_pipeline(state)

    assert result.should_intervene is False
    assert result.final_candidate is None
    assert result.ranked_candidates == []
    assert "cooldown" in (result.decision_reason or "").lower()


@pytest.mark.agents
def test_pipeline_successfully_ranks_and_selects_candidate():
    now = datetime(2026, 3, 16, 18, 0, tzinfo=UTC)
    state = ActivationState(
        user_id=uuid4(),
        current_time=now,
        comfort_level=ComfortLevel.SOLO_OK,
        willingness_radius_km=4.0,
        user_preferences=["art", "community"],
        candidates=[
            _candidate(
                "candidate-strong",
                title="Life drawing social",
                starts_in_minutes=70,
                base_time=now,
                tags=["art", "community"],
                distance_km=1.8,
            ),
            _candidate(
                "candidate-weak",
                title="Far commute event",
                starts_in_minutes=220,
                base_time=now,
                tags=["tech"],
                distance_km=8.5,
            ),
        ],
    )

    result = run_activation_pipeline(state)

    assert result.should_intervene is True
    assert result.final_candidate is not None
    assert result.final_candidate.candidate_id == "candidate-strong"
    assert result.final_candidate.commitment_action is not None
    assert result.final_candidate.social_proof_text is not None
    assert len(result.ranked_candidates) == 1
    assert result.ranked_candidates[0].momentum_score >= result.ranked_candidates[0].relevance_score


@pytest.mark.agents
def test_pipeline_suggests_stage_escalation_on_high_accept_rate():
    now = datetime(2026, 3, 18, 18, 30, tzinfo=UTC)
    state = ActivationState(
        user_id=uuid4(),
        current_time=now,
        activation_stage=ActivationStage.SUGGEST,
        recent_accept_rate=0.82,
        user_preferences=["fitness"],
        candidates=[
            _candidate(
                "candidate-fit",
                title="Park run meetup",
                starts_in_minutes=30,
                base_time=now,
                tags=["fitness", "outdoors"],
                distance_km=1.2,
                tier=OpportunityTier.RECURRING_PATTERN,
            )
        ],
    )

    result = run_activation_pipeline(state)

    assert result.final_candidate is not None
    assert result.suggested_stage == ActivationStage.RECOMMEND
