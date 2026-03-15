from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activation, ActivationResponse, ActivationStage, ComfortLevel, User, UserPreference
from app.utils.llm import extract_tags_from_text

MIN_PREF_WEIGHT = 0.05
MAX_PREF_WEIGHT = 1.0


@dataclass
class FeedbackReview:
    tags: list[str]
    stage_direction: str
    comfort_direction: str
    reason: str


def _clamp_weight(value: float) -> float:
    return max(MIN_PREF_WEIGHT, min(MAX_PREF_WEIGHT, value))


def _next_stage(stage: ActivationStage) -> ActivationStage:
    if stage is ActivationStage.SUGGEST:
        return ActivationStage.RECOMMEND
    if stage is ActivationStage.RECOMMEND:
        return ActivationStage.PRECOMMIT
    if stage is ActivationStage.PRECOMMIT:
        return ActivationStage.ACTIVATE
    return stage


def _previous_stage(stage: ActivationStage) -> ActivationStage:
    if stage is ActivationStage.ACTIVATE:
        return ActivationStage.PRECOMMIT
    if stage is ActivationStage.PRECOMMIT:
        return ActivationStage.RECOMMEND
    if stage is ActivationStage.RECOMMEND:
        return ActivationStage.SUGGEST
    return stage


def _nudge_comfort_towards_solo(level: ComfortLevel) -> ComfortLevel:
    if level is ComfortLevel.NEED_FAMILIAR:
        return ComfortLevel.PREFER_OTHERS
    if level is ComfortLevel.PREFER_OTHERS:
        return ComfortLevel.SOLO_OK
    return level


def _nudge_comfort_towards_support(level: ComfortLevel) -> ComfortLevel:
    if level is ComfortLevel.SOLO_OK:
        return ComfortLevel.PREFER_OTHERS
    if level is ComfortLevel.PREFER_OTHERS:
        return ComfortLevel.NEED_FAMILIAR
    return level


def _normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        value = tag.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _build_review_tags(activation: Activation, feedback_text: str | None) -> list[str]:
    raw_tags: list[str] = []
    if activation.opportunity.event and activation.opportunity.event.tags:
        raw_tags.extend(activation.opportunity.event.tags)

    text_chunks = [
        activation.opportunity.title,
        activation.opportunity.body,
        feedback_text or "",
    ]
    if activation.opportunity.event and activation.opportunity.event.description:
        text_chunks.append(activation.opportunity.event.description)

    inferred = extract_tags_from_text(" ".join(text_chunks), limit=6)
    raw_tags.extend(inferred)
    return _normalize_tags(raw_tags)


def _build_feedback_review(
    activation: Activation,
    *,
    attended: bool,
    rating: int | None,
    feedback_text: str | None,
) -> FeedbackReview:
    positive_experience = attended and (rating is None or rating >= 4)
    negative_experience = (not attended) or (rating is not None and rating <= 2)
    response_was_positive = activation.response is ActivationResponse.ACCEPTED

    tags = _build_review_tags(activation, feedback_text)

    if positive_experience and response_was_positive:
        return FeedbackReview(
            tags=tags,
            stage_direction="up",
            comfort_direction="towards_solo",
            reason="High-confidence positive follow-through.",
        )
    if negative_experience:
        return FeedbackReview(
            tags=tags,
            stage_direction="down",
            comfort_direction="towards_support",
            reason="Low follow-through or low satisfaction.",
        )
    return FeedbackReview(
        tags=tags,
        stage_direction="stay",
        comfort_direction="stay",
        reason="Neutral feedback; keep profile stable.",
    )


def _preference_weight_delta(*, attended: bool, rating: int | None) -> float:
    if attended:
        if rating is None:
            return 0.06
        if rating >= 5:
            return 0.14
        if rating >= 4:
            return 0.1
        if rating >= 3:
            return 0.05
        return 0.02

    if rating is None:
        return -0.08
    if rating <= 2:
        return -0.12
    return -0.06


async def _apply_preference_updates(
    *,
    session: AsyncSession,
    user: User,
    tags: list[str],
    attended: bool,
    rating: int | None,
) -> None:
    if not tags:
        return

    result = await session.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    existing = {preference.category: preference for preference in result.scalars().all()}

    delta = _preference_weight_delta(attended=attended, rating=rating)
    for tag in tags:
        preference = existing.get(tag)
        if preference is None:
            if delta <= 0:
                continue
            session.add(
                UserPreference(
                    user_id=user.id,
                    category=tag,
                    weight=_clamp_weight(0.5 + delta),
                    explicit=False,
                )
            )
            continue

        preference.weight = _clamp_weight(preference.weight + delta)


async def process_post_event_feedback(
    *,
    session: AsyncSession,
    user: User,
    activation: Activation,
    attended: bool,
    rating: int | None,
    feedback_text: str | None,
) -> str:
    review = _build_feedback_review(
        activation,
        attended=attended,
        rating=rating,
        feedback_text=feedback_text,
    )

    await _apply_preference_updates(
        session=session,
        user=user,
        tags=review.tags,
        attended=attended,
        rating=rating,
    )

    if review.stage_direction == "up":
        user.activation_stage = _next_stage(user.activation_stage)
    elif review.stage_direction == "down":
        user.activation_stage = _previous_stage(user.activation_stage)

    if review.comfort_direction == "towards_solo":
        user.comfort_level = _nudge_comfort_towards_solo(user.comfort_level)
    elif review.comfort_direction == "towards_support":
        user.comfort_level = _nudge_comfort_towards_support(user.comfort_level)

    return review.reason
