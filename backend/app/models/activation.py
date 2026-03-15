from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.enums import ActivationResponse

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.user import User


class Activation(Base):
    __tablename__ = "activations"
    __table_args__ = (
        Index("ix_activations_user_shown_at", "user_id", "shown_at"),
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
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    shown_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    response: Mapped[ActivationResponse | None] = mapped_column(
        SqlEnum(
            ActivationResponse,
            name="activation_response",
            values_callable=lambda values: [enum_value.value for enum_value in values],
        ),
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attended: Mapped[bool | None] = mapped_column(Boolean())
    rating: Mapped[int | None] = mapped_column(Integer())
    feedback_text: Mapped[str | None] = mapped_column(Text())

    user: Mapped["User"] = relationship(back_populates="activations")
    opportunity: Mapped["Opportunity"] = relationship(back_populates="activations")
