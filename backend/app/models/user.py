from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text

from app.database import Base
from app.models.enums import ActivationStage, ComfortLevel

if TYPE_CHECKING:
    from app.models.activation import Activation


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    password_hash: Mapped[str | None] = mapped_column(Text())
    location_lat: Mapped[float | None] = mapped_column(Float())
    location_lng: Mapped[float | None] = mapped_column(Float())
    location_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    comfort_level: Mapped[ComfortLevel] = mapped_column(
        SqlEnum(
            ComfortLevel,
            name="comfort_level",
            values_callable=lambda values: [enum_value.value for enum_value in values],
        ),
        nullable=False,
        default=ComfortLevel.SOLO_OK,
        server_default=text("'solo_ok'"),
    )
    willingness_radius_km: Mapped[float] = mapped_column(
        Float(),
        nullable=False,
        default=5.0,
        server_default=text("5"),
    )
    activation_stage: Mapped[ActivationStage] = mapped_column(
        SqlEnum(
            ActivationStage,
            name="activation_stage",
            values_callable=lambda values: [enum_value.value for enum_value in values],
        ),
        nullable=False,
        default=ActivationStage.SUGGEST,
        server_default=text("'suggest'"),
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="UTC",
        server_default=text("'UTC'"),
    )
    push_subscription: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    preferences: Mapped[list["UserPreference"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    activations: Mapped[list["Activation"]] = relationship(back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_user_preferences_user_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    weight: Mapped[float] = mapped_column(
        Float(),
        nullable=False,
        default=0.5,
        server_default=text("0.5"),
    )
    explicit: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    user: Mapped[User] = relationship(back_populates="preferences")

