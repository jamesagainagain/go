from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ActivationResponse, ActivationStage
from app.schemas.opportunity import Opportunity


class ActivationCheckRequest(BaseModel):
    lat: float | None = None
    lng: float | None = None


class ActivationCardResponse(BaseModel):
    activation_id: UUID
    opportunity: Opportunity
    stage: ActivationStage
    expires_at: datetime


class NoOpportunityResponse(BaseModel):
    activation_id: None = None
    opportunity: None = None
    message: str = "No suitable opportunity right now"


class ActivationRespondRequest(BaseModel):
    response: ActivationResponse


class FeedbackRequest(BaseModel):
    attended: bool
    rating: int | None = Field(default=None, ge=1, le=5)
    feedback_text: str | None = None


class ActivationHistoryItem(BaseModel):
    id: UUID
    opportunity: Opportunity
    shown_at: datetime
    response: ActivationResponse | None = None
    attended: bool | None = None
    rating: int | None = None
    feedback_text: str | None = None


class ActivationHistoryResponse(BaseModel):
    items: list[ActivationHistoryItem]
    total: int
