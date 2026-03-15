from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OpportunityTier
from app.schemas.opportunity import VenueSummary


class EventSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    cost_pence: int | None = None
    tags: list[str] = Field(default_factory=list)
    venue: VenueSummary | None = None
    tier: OpportunityTier


class EventsNearbyResponse(BaseModel):
    events: list[EventSummary]
