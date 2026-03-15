from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.enums import OpportunityTier

if TYPE_CHECKING:
    from app.models.activation import Activation
    from app.models.event import Event


class Opportunity(Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        Index("ix_opportunities_location", "location", postgresql_using="gist"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="SET NULL"),
    )
    tier: Mapped[OpportunityTier] = mapped_column(
        SqlEnum(
            OpportunityTier,
            name="opportunity_tier",
            values_callable=lambda values: [enum_value.value for enum_value in values],
        ),
        nullable=False,
        default=OpportunityTier.STRUCTURED,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text(), nullable=False)
    walk_minutes: Mapped[int | None] = mapped_column(Integer())
    travel_description: Mapped[str | None] = mapped_column(Text())
    social_proof_text: Mapped[str | None] = mapped_column(Text())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    event: Mapped["Event | None"] = relationship(back_populates="opportunities")
    activations: Mapped[list["Activation"]] = relationship(back_populates="opportunity")
