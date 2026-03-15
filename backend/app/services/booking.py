from __future__ import annotations

from typing import Protocol

from app.models.enums import OpportunityTier
from app.schemas.opportunity import CommitmentAction


class BookingProvider(Protocol):
    def build_action(
        self,
        *,
        tier: OpportunityTier,
        source_url: str | None = None,
    ) -> CommitmentAction:
        ...


class DefaultBookingProvider:
    def build_action(
        self,
        *,
        tier: OpportunityTier,
        source_url: str | None = None,
    ) -> CommitmentAction:
        if source_url:
            return CommitmentAction(type="deep_link", label="Open booking", url=source_url)

        if tier in {OpportunityTier.MICRO_COORDINATION, OpportunityTier.RECURRING_PATTERN}:
            return CommitmentAction(type="internal_going", label="I'm going")

        if tier is OpportunityTier.SOLO_NUDGE:
            return CommitmentAction(type="none", label="Looks good")

        return CommitmentAction(type="one_tap_rsvp", label="Hold my spot")


def build_commitment_action(
    *,
    tier: OpportunityTier,
    source_url: str | None = None,
    provider: BookingProvider | None = None,
) -> CommitmentAction:
    booking_provider = provider or DefaultBookingProvider()
    return booking_provider.build_action(tier=tier, source_url=source_url)
