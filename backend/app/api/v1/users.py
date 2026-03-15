from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models import User, UserPreference
from app.models.enums import ComfortLevel
from app.schemas.user import (
    LocationUpdateRequest,
    Preference,
    VoiceIntakeRequest,
    VoiceIntakeResponse,
    UserProfile,
    UserUpdateRequest,
)
from app.utils.llm import extract_tags_from_text
from app.utils.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
RADIUS_KM_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:km|kilometers?|kilometres?)")
RADIUS_MIN_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:min|mins|minutes?)")


def _to_user_profile(user: User) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        comfort_level=user.comfort_level,
        willingness_radius_km=user.willingness_radius_km,
        activation_stage=user.activation_stage,
        timezone=user.timezone,
        location_lat=user.location_lat,
        location_lng=user.location_lng,
        location_updated_at=user.location_updated_at,
        preferences=[
            Preference(category=p.category, weight=p.weight, explicit=p.explicit)
            for p in user.preferences
        ],
        created_at=user.created_at,
    )


def _normalize_categories(categories: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for category in categories:
        value = category.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _infer_comfort_level(transcript: str) -> ComfortLevel | None:
    lowered = transcript.lower()
    need_familiar_signals = (
        "need familiar",
        "not comfortable alone",
        "don't want to go alone",
        "dont want to go alone",
        "need a friend",
    )
    if any(signal in lowered for signal in need_familiar_signals):
        return ComfortLevel.NEED_FAMILIAR

    solo_ok_signals = (
        "happy going solo",
        "fine going solo",
        "comfortable alone",
        "i can go alone",
    )
    if any(signal in lowered for signal in solo_ok_signals):
        return ComfortLevel.SOLO_OK

    prefer_others_signals = (
        "prefer others",
        "prefer people around",
        "rather go with people",
        "group vibes",
    )
    if any(signal in lowered for signal in prefer_others_signals):
        return ComfortLevel.PREFER_OTHERS
    return None


def _infer_radius_km(transcript: str) -> float | None:
    lowered = transcript.lower()
    km_match = RADIUS_KM_PATTERN.search(lowered)
    if km_match:
        km_value = float(km_match.group(1))
        return max(0.5, min(km_value, 20.0))

    min_match = RADIUS_MIN_PATTERN.search(lowered)
    if min_match:
        minutes = float(min_match.group(1))
        km_value = minutes / 12.0
        return max(0.5, min(km_value, 20.0))
    return None


async def _upsert_voice_preferences(
    *,
    session: AsyncSession,
    current_user: User,
    inferred_categories: list[str],
) -> None:
    if not inferred_categories:
        return

    existing_by_category = {preference.category: preference for preference in current_user.preferences}
    for category in inferred_categories:
        existing = existing_by_category.get(category)
        if existing is None:
            session.add(
                UserPreference(
                    user_id=current_user.id,
                    category=category,
                    weight=0.7,
                    explicit=False,
                )
            )
            continue
        existing.weight = min(1.0, max(existing.weight, 0.65) + 0.05)


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)) -> UserProfile:
    return _to_user_profile(current_user)


@router.patch("/me", response_model=UserProfile)
async def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> UserProfile:
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.comfort_level is not None:
        current_user.comfort_level = payload.comfort_level
    if payload.willingness_radius_km is not None:
        current_user.willingness_radius_km = payload.willingness_radius_km
    if payload.timezone is not None:
        current_user.timezone = payload.timezone

    if payload.preferences is not None:
        await session.execute(
            delete(UserPreference).where(UserPreference.user_id == current_user.id)
        )
        for pref in payload.preferences:
            session.add(
                UserPreference(
                    user_id=current_user.id,
                    category=pref.category,
                    weight=pref.weight,
                    explicit=pref.explicit,
                )
            )

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if "uq_user_preferences_user_category" in str(error.orig):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duplicate preference categories are not allowed.",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data.",
        ) from error

    result = await session.execute(
        select(User).options(selectinload(User.preferences)).where(User.id == current_user.id)
    )
    user = result.scalar_one()
    return _to_user_profile(user)


@router.post("/me/location")
async def update_location(
    payload: LocationUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    current_user.location_lat = payload.lat
    current_user.location_lng = payload.lng
    current_user.location_updated_at = datetime.now(UTC)
    await session.commit()
    return {"status": "ok"}


@router.post("/me/voice-intake", response_model=VoiceIntakeResponse)
async def voice_intake(
    payload: VoiceIntakeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> VoiceIntakeResponse:
    inferred_categories = _normalize_categories(extract_tags_from_text(payload.transcript, limit=6))
    await _upsert_voice_preferences(
        session=session,
        current_user=current_user,
        inferred_categories=inferred_categories,
    )

    inferred_comfort_level = _infer_comfort_level(payload.transcript)
    if inferred_comfort_level is not None:
        current_user.comfort_level = inferred_comfort_level

    inferred_radius_km = _infer_radius_km(payload.transcript)
    if inferred_radius_km is not None:
        current_user.willingness_radius_km = inferred_radius_km

    await session.commit()
    result = await session.execute(
        select(User)
        .options(selectinload(User.preferences))
        .where(User.id == current_user.id)
        .execution_options(populate_existing=True)
    )
    user = result.scalar_one()
    inferred_preferences_result = await session.execute(
        select(UserPreference).where(
            UserPreference.user_id == current_user.id,
            UserPreference.category.in_(inferred_categories),
        )
    )
    inferred_preferences_rows = inferred_preferences_result.scalars().all()
    inferred_preferences = [
        Preference(
            category=preference.category,
            weight=preference.weight,
            explicit=preference.explicit,
        )
        for preference in inferred_preferences_rows
    ]
    return VoiceIntakeResponse(
        status="ok",
        source=payload.source,
        inferred_preferences=inferred_preferences,
        profile=_to_user_profile(user),
    )
