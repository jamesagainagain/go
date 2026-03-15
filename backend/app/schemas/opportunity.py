from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OpportunityTier


class VenueSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    lat: float
    lng: float
    address: str | None = None


class SocialProof(BaseModel):
    text: str | None = None
    total_expected: int | None = None
    solo_count: int | None = None
    familiar_face: bool | None = None


class CommitmentAction(BaseModel):
    type: str = Field(pattern="^(one_tap_rsvp|deep_link|internal_going|none)$")
    label: str | None = None
    url: str | None = None


class Opportunity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    body: str
    tier: OpportunityTier
    walk_minutes: int
    travel_description: str
    starts_at: datetime
    leave_by: datetime
    cost_pence: int
    venue: VenueSummary
    social_proof: SocialProof | None = None
    commitment_action: CommitmentAction | None = None
    route_polyline: str | None = None
