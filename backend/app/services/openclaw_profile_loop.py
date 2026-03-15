from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User, UserPreference
from app.services.openclaw import build_openclaw_provider

PROFILE_SYNC_COOLDOWN: Final[timedelta] = timedelta(minutes=20)
_last_profile_sync: dict[UUID, datetime] = {}


def _normalize_interest_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        value = tag.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


async def _upsert_inferred_preferences(
    *,
    session: AsyncSession,
    user: User,
    tags: list[str],
) -> int:
    if not tags:
        return 0

    result = await session.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    existing = {preference.category: preference for preference in result.scalars().all()}

    updated = 0
    for tag in tags:
        preference = existing.get(tag)
        if preference is None:
            session.add(
                UserPreference(
                    user_id=user.id,
                    category=tag,
                    weight=0.6,
                    explicit=False,
                )
            )
            updated += 1
            continue
        preference.weight = min(1.0, round(preference.weight + 0.04, 2))
        updated += 1
    return updated


def _should_sync(user_id: UUID, now: datetime) -> bool:
    last = _last_profile_sync.get(user_id)
    if last is None:
        return True
    return now - last >= PROFILE_SYNC_COOLDOWN


async def maybe_apply_openclaw_profile_updates(
    *,
    session: AsyncSession,
    user: User,
    city: str = "london",
    hours_ahead: int = 8,
) -> str | None:
    settings = get_settings()
    if not settings.openclaw_enabled:
        return None

    now = datetime.now(UTC)
    if not _should_sync(user.id, now):
        return None

    provider = build_openclaw_provider(
        enabled=settings.openclaw_enabled,
        endpoint=settings.openclaw_endpoint,
        api_token=settings.openclaw_api_token or settings.openai_api_key,
        timeout_seconds=min(3.0, settings.openclaw_timeout_seconds),
        model=settings.openai_model_fast,
    )
    suggestions = await provider.fetch_suggestions(city=city, hours_ahead=hours_ahead)
    interest_tags: list[str] = []
    for suggestion in suggestions:
        if suggestion.tags:
            interest_tags.extend(suggestion.tags)
        if suggestion.category:
            interest_tags.append(suggestion.category)

    tags = _normalize_interest_tags(interest_tags)
    if not tags:
        _last_profile_sync[user.id] = now
        return None

    updated = await _upsert_inferred_preferences(session=session, user=user, tags=tags)
    _last_profile_sync[user.id] = now
    if updated == 0:
        return None
    return f"OpenClaw updated {updated} inferred profile signals."
