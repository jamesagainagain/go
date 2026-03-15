from __future__ import annotations

from datetime import timedelta

from app.agents.types import ActivationState


def run_context_agent(
    state: ActivationState,
    *,
    intervention_threshold: float = 0.4,
    cooldown_minutes: int = 120,
) -> ActivationState:
    score = 0.0
    now = state.current_time
    hour = now.hour

    is_post_work_window = 17 <= hour <= 19
    is_weekend_morning = now.weekday() >= 5 and 9 <= hour <= 11
    if is_post_work_window or is_weekend_morning:
        score += 0.5
    else:
        score += 0.2

    cooldown_ok = True
    if state.last_nudge_at is None:
        score += 0.3
    else:
        delta = now - state.last_nudge_at
        if delta >= timedelta(minutes=cooldown_minutes):
            score += 0.3
        else:
            cooldown_ok = False
            score -= 0.45

    if state.user_preferences:
        score += 0.2

    score = max(0.0, min(score, 1.0))
    should_intervene = cooldown_ok and score >= intervention_threshold
    reason = (
        "High-leverage intervention window detected."
        if should_intervene
        else "Skipped due to cooldown or low intervention score."
    )

    state.intervention_score = score
    state.should_intervene = should_intervene
    state.decision_reason = reason
    return state
