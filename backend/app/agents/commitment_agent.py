from __future__ import annotations

from app.agents.types import ActivationState
from app.services.booking import build_commitment_action


def run_commitment_agent(state: ActivationState) -> ActivationState:
    if not state.should_intervene:
        return state

    source_candidates = state.enriched_candidates or state.candidates
    for candidate in source_candidates:
        candidate.commitment_action = build_commitment_action(
            tier=candidate.tier,
            source_url=candidate.source_url,
        )
    state.enriched_candidates = source_candidates
    return state
