from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ActivationStage, ComfortLevel, OpportunityTier


class AgentCommitmentAction(BaseModel):
    type: str
    label: str | None = None
    url: str | None = None


class ActivationCandidate(BaseModel):
    candidate_id: str
    title: str
    body: str
    tier: OpportunityTier
    starts_at: datetime
    walk_minutes: int = 10
    travel_description: str = "Short walk"
    distance_km: float | None = None
    tags: list[str] = Field(default_factory=list)
    source_url: str | None = None
    cost_pence: int = 0
    expected_attendees: int | None = None
    solo_count: int | None = None
    social_proof_text: str | None = None
    relevance_score: float = 0.0
    momentum_score: float = 0.0
    commitment_action: AgentCommitmentAction | None = None


class ActivationState(BaseModel):
    user_id: UUID
    current_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_lat: float | None = None
    user_lng: float | None = None
    comfort_level: ComfortLevel = ComfortLevel.SOLO_OK
    activation_stage: ActivationStage = ActivationStage.SUGGEST
    willingness_radius_km: float = 5.0
    user_preferences: list[str] = Field(default_factory=list)
    last_nudge_at: datetime | None = None
    recent_accept_rate: float | None = None
    candidates: list[ActivationCandidate] = Field(default_factory=list)
    enriched_candidates: list[ActivationCandidate] = Field(default_factory=list)
    ranked_candidates: list[ActivationCandidate] = Field(default_factory=list)
    final_candidate: ActivationCandidate | None = None
    intervention_score: float = 0.0
    should_intervene: bool = False
    suggested_stage: ActivationStage | None = None
    decision_reason: str | None = None
