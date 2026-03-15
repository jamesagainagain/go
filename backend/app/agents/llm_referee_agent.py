from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.agents.types import ActivationCandidate, ActivationState
from app.config import get_settings


def _build_candidates_payload(candidates: list[ActivationCandidate]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for candidate in candidates:
        payload.append(
            {
                "candidate_id": candidate.candidate_id,
                "title": candidate.title,
                "body": candidate.body,
                "tier": candidate.tier.value,
                "starts_at": candidate.starts_at.isoformat(),
                "walk_minutes": candidate.walk_minutes,
                "distance_km": candidate.distance_km,
                "tags": candidate.tags,
                "cost_pence": candidate.cost_pence,
                "expected_attendees": candidate.expected_attendees,
                "solo_count": candidate.solo_count,
                "relevance_score": candidate.relevance_score,
                "momentum_score": candidate.momentum_score,
                "social_proof_text": candidate.social_proof_text,
            }
        )
    return payload


def _choose_candidate_id_with_llm(
    *,
    state: ActivationState,
    candidates: list[ActivationCandidate],
    prompts: dict[str, str],
) -> tuple[str | None, str | None]:
    settings = get_settings()
    if not settings.openai_api_key:
        return None, None

    client = OpenAI(api_key=settings.openai_api_key, timeout=4.0)

    system_prompt = (
        "You are the final referee in FirstMove's activation pipeline.\n"
        "Pick exactly one candidate_id that is most likely to convert to real attendance.\n"
        "Respect low-friction commitment and social confidence principles.\n\n"
        f"Context guidance:\n{prompts.get('context', '')}\n\n"
        f"Discovery guidance:\n{prompts.get('discovery', '')}\n\n"
        f"Social proof guidance:\n{prompts.get('social_proof', '')}\n\n"
        f"Commitment guidance:\n{prompts.get('commitment', '')}\n\n"
        f"Momentum guidance:\n{prompts.get('momentum', '')}\n\n"
        'Return strict JSON only: {"candidate_id":"...", "reason":"..."}'
    )

    user_payload = {
        "user_context": {
            "comfort_level": state.comfort_level.value,
            "activation_stage": state.activation_stage.value,
            "willingness_radius_km": state.willingness_radius_km,
            "user_preferences": state.user_preferences,
            "recent_accept_rate": state.recent_accept_rate,
        },
        "candidates": _build_candidates_payload(candidates),
    }

    response = client.chat.completions.create(
        model=settings.openai_model_fast,
        temperature=0.1,
        max_tokens=120,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
    )
    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)
    selected_id = parsed.get("candidate_id")
    reason = parsed.get("reason")
    if isinstance(selected_id, str):
        return selected_id, reason if isinstance(reason, str) else None
    return None, None


def run_llm_referee_agent(state: ActivationState, *, prompts: dict[str, str]) -> ActivationState:
    source_candidates = state.ranked_candidates or state.enriched_candidates or state.candidates
    if not state.should_intervene or not source_candidates:
        return state

    top_candidates = source_candidates[:3]
    if len(top_candidates) <= 1:
        return state

    try:
        selected_id, reason = _choose_candidate_id_with_llm(
            state=state,
            candidates=top_candidates,
            prompts=prompts,
        )
    except Exception:
        return state

    if not selected_id:
        return state

    selected = next(
        (candidate for candidate in top_candidates if candidate.candidate_id == selected_id),
        None,
    )
    if selected is None:
        return state

    state.final_candidate = selected
    if reason:
        state.decision_reason = f"LLM referee selected candidate: {reason}"
    else:
        state.decision_reason = "LLM referee selected final candidate."
    return state
