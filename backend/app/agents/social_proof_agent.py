from __future__ import annotations

from app.agents.types import ActivationState


def run_social_proof_agent(state: ActivationState) -> ActivationState:
    if not state.should_intervene or not state.candidates:
        state.enriched_candidates = []
        return state

    enriched = []
    for candidate in state.candidates:
        expected = candidate.expected_attendees if candidate.expected_attendees is not None else 4
        solo = candidate.solo_count if candidate.solo_count is not None else max(1, expected // 3)
        candidate.expected_attendees = expected
        candidate.solo_count = min(solo, expected)
        if not candidate.social_proof_text:
            candidate.social_proof_text = f"{candidate.solo_count} others going solo"
        enriched.append(candidate)

    state.enriched_candidates = enriched
    return state
