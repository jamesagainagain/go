from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.agents.llm_referee_agent import run_llm_referee_agent
from app.agents.types import ActivationCandidate, ActivationState
from app.models.enums import OpportunityTier


def _candidate(candidate_id: str, title: str, starts_at: datetime) -> ActivationCandidate:
    return ActivationCandidate(
        candidate_id=candidate_id,
        title=title,
        body=f"{title} body",
        tier=OpportunityTier.STRUCTURED,
        starts_at=starts_at,
        walk_minutes=10,
        travel_description="10 min walk",
        relevance_score=0.6,
        momentum_score=0.7,
    )


@pytest.mark.agents
def test_llm_referee_keeps_existing_choice_on_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime(2026, 3, 15, 18, 0, tzinfo=UTC)
    strong = _candidate("strong", "Strong candidate", now + timedelta(minutes=45))
    weak = _candidate("weak", "Weak candidate", now + timedelta(minutes=90))
    state = ActivationState(
        user_id=uuid4(),
        current_time=now,
        should_intervene=True,
        ranked_candidates=[strong, weak],
        final_candidate=strong,
    )

    def _raise_error(**_: object) -> tuple[str | None, str | None]:
        raise RuntimeError("simulated llm failure")

    monkeypatch.setattr("app.agents.llm_referee_agent._choose_candidate_id_with_llm", _raise_error)

    result = run_llm_referee_agent(state, prompts={})

    assert result.final_candidate is not None
    assert result.final_candidate.candidate_id == "strong"


@pytest.mark.agents
def test_llm_referee_can_override_final_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime(2026, 3, 15, 18, 0, tzinfo=UTC)
    strong = _candidate("strong", "Strong candidate", now + timedelta(minutes=45))
    weak = _candidate("weak", "Weak candidate", now + timedelta(minutes=90))
    state = ActivationState(
        user_id=uuid4(),
        current_time=now,
        should_intervene=True,
        ranked_candidates=[strong, weak],
        final_candidate=strong,
    )

    def _pick_weak(**_: object) -> tuple[str | None, str | None]:
        return "weak", "Lower friction for this user right now."

    monkeypatch.setattr("app.agents.llm_referee_agent._choose_candidate_id_with_llm", _pick_weak)

    result = run_llm_referee_agent(state, prompts={})

    assert result.final_candidate is not None
    assert result.final_candidate.candidate_id == "weak"
    assert "LLM referee selected candidate" in (result.decision_reason or "")
