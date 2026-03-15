from __future__ import annotations

from datetime import timedelta

from app.agents.types import ActivationCandidate, ActivationState


def _score_candidate(state: ActivationState, candidate: ActivationCandidate) -> float:
    preference_overlap = len(set(state.user_preferences).intersection(set(candidate.tags)))
    preference_score = min(preference_overlap * 0.15, 0.45)
    distance_score = 0.15
    if candidate.distance_km is not None:
        if candidate.distance_km <= state.willingness_radius_km:
            distance_score = 0.2
        else:
            distance_score = 0.05

    time_delta = candidate.starts_at - state.current_time
    starts_soon_bonus = 0.1 if timedelta(minutes=0) <= time_delta <= timedelta(hours=2) else 0.0
    return max(0.0, min(1.0, 0.3 + preference_score + distance_score + starts_soon_bonus))


def run_discovery_agent(state: ActivationState) -> ActivationState:
    if not state.should_intervene:
        return state

    upper_window = state.current_time + timedelta(hours=6)
    filtered_candidates: list[ActivationCandidate] = []
    for candidate in state.candidates:
        if candidate.starts_at < state.current_time:
            continue
        if candidate.starts_at > upper_window:
            continue
        if (
            candidate.distance_km is not None
            and candidate.distance_km > state.willingness_radius_km + 1.0
        ):
            continue
        candidate.relevance_score = _score_candidate(state, candidate)
        filtered_candidates.append(candidate)

    filtered_candidates.sort(key=lambda item: item.relevance_score, reverse=True)
    state.candidates = filtered_candidates
    if not filtered_candidates:
        state.decision_reason = "No opportunities passed discovery filters."
    return state
