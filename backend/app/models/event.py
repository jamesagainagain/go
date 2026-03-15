from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.enums import OpportunityTier

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.venue import Venue


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_starts_at", "starts_at"),
        Index("ix_events_tier", "tier"),
        Index("ix_events_tags", "tags", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    venue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("venues.id", ondelete="SET NULL"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tier: Mapped[OpportunityTier] = mapped_column(
        SqlEnum(
            OpportunityTier,
            name="opportunity_tier",
            values_callable=lambda values: [enum_value.value for enum_value in values],
        ),
        nullable=False,
        default=OpportunityTier.STRUCTURED,
    )
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text())
    cost_pence: Mapped[int | None] = mapped_column(Integer(), server_default=text("0"))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String(64)))
    attendee_count_estimate: Mapped[int | None] = mapped_column(Integer())
    solo_friendly_score: Mapped[float | None] = mapped_column(Float())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    venue: Mapped["Venue | None"] = relationship(back_populates="events")
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="event")
