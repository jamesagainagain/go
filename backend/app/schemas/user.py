from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import ActivationStage, ComfortLevel


class PreferenceInput(BaseModel):
    category: str
    weight: float = Field(default=0.5, ge=0, le=1)
    explicit: bool = True

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Preference category cannot be empty.")
        return normalized


class Preference(BaseModel):
    category: str
    weight: float = Field(ge=0, le=1)
    explicit: bool


def _validate_unique_preferences(
    preferences: list[PreferenceInput] | None,
) -> list[PreferenceInput] | None:
    if preferences is None:
        return None

    seen_categories: set[str] = set()
    duplicate_categories: set[str] = set()
    for preference in preferences:
        if preference.category in seen_categories:
            duplicate_categories.add(preference.category)
            continue
        seen_categories.add(preference.category)

    if duplicate_categories:
        duplicates = ", ".join(sorted(duplicate_categories))
        raise ValueError(f"Duplicate preference categories are not allowed: {duplicates}")

    return preferences


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=8)
    comfort_level: ComfortLevel | None = None
    preferences: list[PreferenceInput] | None = None
    timezone: str = "Europe/London"

    @field_validator("preferences")
    @classmethod
    def validate_unique_preferences(
        cls,
        value: list[PreferenceInput] | None,
    ) -> list[PreferenceInput] | None:
        return _validate_unique_preferences(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str | None = None
    comfort_level: ComfortLevel | None = None
    willingness_radius_km: float | None = None
    activation_stage: ActivationStage | None = None
    timezone: str | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    location_updated_at: datetime | None = None
    preferences: list[Preference] = Field(default_factory=list)
    created_at: datetime | None = None


class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    comfort_level: ComfortLevel | None = None
    willingness_radius_km: float | None = None
    timezone: str | None = None
    preferences: list[PreferenceInput] | None = None

    @field_validator("preferences")
    @classmethod
    def validate_unique_preferences(
        cls,
        value: list[PreferenceInput] | None,
    ) -> list[PreferenceInput] | None:
        return _validate_unique_preferences(value)


class LocationUpdateRequest(BaseModel):
    lat: float
    lng: float


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
