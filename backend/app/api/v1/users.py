from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models import User, UserPreference
from app.schemas.user import (
    LocationUpdateRequest,
    Preference,
    UserProfile,
    UserUpdateRequest,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


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
