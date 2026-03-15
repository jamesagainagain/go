from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import ActivationStage, ComfortLevel


class PreferenceInput(BaseModel):
    category: str
    weight: float = Field(default=0.5, ge=0, le=1)
    explicit: bool = True


class Preference(BaseModel):
    category: str
    weight: float = Field(ge=0, le=1)
    explicit: bool


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8)
    comfort_level: ComfortLevel | None = None
    preferences: list[PreferenceInput] | None = None
    timezone: str = "Europe/London"


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


class LocationUpdateRequest(BaseModel):
    lat: float
    lng: float


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
