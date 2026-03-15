from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models import User, UserPreference
from app.models.enums import ComfortLevel
from app.schemas.user import (
    AuthResponse,
    LoginRequest,
    Preference,
    RegisterRequest,
    UserProfile,
)
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _map_integrity_error_to_http(error: IntegrityError) -> HTTPException:
    message = str(error.orig)
    if "users_email_key" in message:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    if "uq_user_preferences_user_category" in message:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate preference categories are not allowed.",
        )
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid request data.",
    )


def _to_user_profile(user: User) -> UserProfile:
    preferences = [
        Preference(category=p.category, weight=p.weight, explicit=p.explicit)
        for p in user.preferences
    ]
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
        preferences=preferences,
        created_at=user.created_at,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    existing_user = await session.execute(select(User).where(User.email == payload.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=str(payload.email),
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        comfort_level=payload.comfort_level or ComfortLevel.SOLO_OK,
        timezone=payload.timezone,
    )
    session.add(user)
    try:
        await session.flush()

        if payload.preferences:
            for pref in payload.preferences:
                session.add(
                    UserPreference(
                        user_id=user.id,
                        category=pref.category,
                        weight=pref.weight,
                        explicit=pref.explicit,
                    )
                )

        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise _map_integrity_error_to_http(error) from error

    result = await session.execute(
        select(User).options(selectinload(User.preferences)).where(User.id == user.id)
    )
    user = result.scalar_one()

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, token_type="bearer", user=_to_user_profile(user))


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    result = await session.execute(
        select(User).options(selectinload(User.preferences)).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, token_type="bearer", user=_to_user_profile(user))
