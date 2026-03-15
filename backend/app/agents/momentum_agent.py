from __future__ import annotations

from app.agents.types import ActivationCandidate, ActivationState
from app.models.enums import ActivationStage, ComfortLevel


def _momentum_score(state: ActivationState, candidate: ActivationCandidate) -> float:
    score = candidate.relevance_score

    if candidate.walk_minutes <= 15:
        score += 0.15
    elif candidate.walk_minutes <= 25:
        score += 0.05

    if candidate.solo_count:
        if state.comfort_level is ComfortLevel.SOLO_OK:
            score += min(0.2, candidate.solo_count / 20)
        if state.comfort_level is ComfortLevel.NEED_FAMILIAR and candidate.solo_count >= 2:
            score += 0.08

    if candidate.expected_attendees:
        score += min(0.12, candidate.expected_attendees / 100)

    return max(0.0, min(score, 1.0))


def _next_stage(current: ActivationStage) -> ActivationStage:
    if current is ActivationStage.SUGGEST:
        return ActivationStage.RECOMMEND
    if current is ActivationStage.RECOMMEND:
        return ActivationStage.PRECOMMIT
    return current


def run_momentum_agent(state: ActivationState) -> ActivationState:
    source_candidates = state.enriched_candidates or state.candidates
    if not state.should_intervene or not source_candidates:
        state.ranked_candidates = []
        state.final_candidate = None
        if state.decision_reason is None:
            state.decision_reason = "No candidates to rank."
        return state

    for candidate in source_candidates:
        candidate.momentum_score = _momentum_score(state, candidate)
    ranked = sorted(source_candidates, key=lambda item: item.momentum_score, reverse=True)
    state.ranked_candidates = ranked
    state.final_candidate = ranked[0]
    state.decision_reason = "Momentum agent selected highest-conversion candidate."

    if (state.recent_accept_rate or 0) >= 0.7:
        state.suggested_stage = _next_stage(state.activation_stage)
    else:
        state.suggested_stage = state.activation_stage
    return state
