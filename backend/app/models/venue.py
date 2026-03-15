from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.event import Event


class Venue(Base):
    __tablename__ = "venues"
    __table_args__ = (
        Index("ix_venues_location", "location", postgresql_using="gist"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text())
    location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False),
    )
    venue_type: Mapped[str | None] = mapped_column(String(64))
    capacity_estimate: Mapped[int | None] = mapped_column(Integer())
    vibe_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String(64)))
    source_url: Mapped[str | None] = mapped_column(Text())

    events: Mapped[list["Event"]] = relationship(back_populates="venue")
