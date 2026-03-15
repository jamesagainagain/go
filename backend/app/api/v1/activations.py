from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.orchestrator import run_activation_pipeline
from app.agents.types import ActivationCandidate, ActivationState
from app.database import get_db_session
from app.models import Activation, ActivationResponse, Event, Opportunity, OpportunityTier, User
from app.schemas.activation import (
    ActivationCardResponse,
    ActivationCheckRequest,
    ActivationHistoryItem,
    ActivationHistoryResponse,
    ActivationRespondRequest,
    NoOpportunityResponse,
)
from app.schemas.opportunity import Opportunity as OpportunitySchema
from app.schemas.opportunity import SocialProof, VenueSummary
from app.services.booking import build_commitment_action
from app.utils.security import get_current_user

router = APIRouter(prefix="/activations", tags=["activations"])

LONDON_FALLBACK_LAT = 51.5074
LONDON_FALLBACK_LNG = -0.1278
FALLBACK_OPPORTUNITY_TITLE = "Take a short reset walk"


def _extract_solo_count(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"(\d+)\s+others?\s+going\s+solo", text.lower())
    if match is None:
        return None
    return int(match.group(1))


async def _load_venue_coordinates(
    *,
    session: AsyncSession,
    venue_id: UUID | None,
    cache: dict[UUID, tuple[float | None, float | None]] | None = None,
) -> tuple[float | None, float | None]:
    if venue_id is None:
        return None, None

    if cache is not None and venue_id in cache:
        return cache[venue_id]

    result = await session.execute(
        text(
            """
            SELECT
                ST_Y(location::geometry) AS lat,
                ST_X(location::geometry) AS lng
            FROM venues
            WHERE id = :venue_id
              AND location IS NOT NULL
            LIMIT 1
            """
        ),
        {"venue_id": str(venue_id)},
    )
    row = result.mappings().first()
    if not row:
        if cache is not None:
            cache[venue_id] = (None, None)
        return None, None
    lat_lng = (float(row["lat"]), float(row["lng"]))
    if cache is not None:
        cache[venue_id] = lat_lng
    return lat_lng


async def _build_venue_summary(
    *,
    session: AsyncSession,
    event: Event | None,
    fallback_lat: float,
    fallback_lng: float,
    venue_coordinates_cache: dict[UUID, tuple[float | None, float | None]] | None = None,
) -> VenueSummary:
    if event and event.venue:
        venue_lat, venue_lng = await _load_venue_coordinates(
            session=session,
            venue_id=event.venue.id,
            cache=venue_coordinates_cache,
        )
        return VenueSummary(
            name=event.venue.name,
            lat=venue_lat if venue_lat is not None else fallback_lat,
            lng=venue_lng if venue_lng is not None else fallback_lng,
            address=event.venue.address,
        )
    return VenueSummary(name="London Venue", lat=fallback_lat, lng=fallback_lng, address=None)


async def _build_social_proof(
    *,
    session: AsyncSession,
    opportunity: Opportunity,
) -> SocialProof:
    accepted_count = await session.scalar(
        select(func.count(Activation.id)).where(
            Activation.opportunity_id == opportunity.id,
            Activation.response == ActivationResponse.ACCEPTED,
        )
    )
    solo_count = _extract_solo_count(opportunity.social_proof_text)
    total_expected = int(accepted_count or 0)
    if total_expected == 0 and solo_count is not None:
        total_expected = solo_count
    return SocialProof(
        text=opportunity.social_proof_text,
        total_expected=total_expected if total_expected > 0 else None,
        solo_count=solo_count,
        familiar_face=False,
    )


async def _to_opportunity_schema(
    *,
    session: AsyncSession,
    opportunity: Opportunity,
    fallback_lat: float,
    fallback_lng: float,
    venue_coordinates_cache: dict[UUID, tuple[float | None, float | None]] | None = None,
) -> OpportunitySchema:
    event = opportunity.event
    walk_minutes = opportunity.walk_minutes or 12
    starts_at = event.starts_at if event else opportunity.expires_at
    leave_by = starts_at - timedelta(minutes=walk_minutes)
    source_url = event.source_url if event else None
    venue = await _build_venue_summary(
        session=session,
        event=event,
        fallback_lat=fallback_lat,
        fallback_lng=fallback_lng,
        venue_coordinates_cache=venue_coordinates_cache,
    )
    social_proof = await _build_social_proof(session=session, opportunity=opportunity)
    return OpportunitySchema(
        title=opportunity.title,
        body=opportunity.body,
        tier=opportunity.tier,
        walk_minutes=walk_minutes,
        travel_description=opportunity.travel_description or f"{walk_minutes} min walk",
        starts_at=starts_at,
        leave_by=leave_by,
        cost_pence=event.cost_pence or 0 if event else 0,
        venue=venue,
        social_proof=social_proof,
        commitment_action=build_commitment_action(tier=opportunity.tier, source_url=source_url),
        route_polyline=None,
    )


async def _find_pending_activation(
    *,
    session: AsyncSession,
    user_id: UUID,
) -> Activation | None:
    now = datetime.now(UTC)
    result = await session.execute(
        select(Activation)
        .join(Activation.opportunity)
        .where(
            Activation.user_id == user_id,
            Activation.response.is_(None),
            Opportunity.expires_at > now,
        )
        .order_by(Activation.shown_at.desc())
        .options(
            selectinload(Activation.opportunity)
            .selectinload(Opportunity.event)
            .selectinload(Event.venue)
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _find_candidate_opportunity(
    *,
    session: AsyncSession,
    current_user: User,
) -> Opportunity | None:
    now = datetime.now(UTC)
    result = await session.execute(
        select(Opportunity)
        .where(Opportunity.expires_at > now)
        .order_by(Opportunity.expires_at.asc())
        .options(selectinload(Opportunity.event).selectinload(Event.venue))
        .limit(25)
    )
    opportunities = result.scalars().all()
    if not opportunities:
        return None

    candidates = [
        ActivationCandidate(
            candidate_id=str(opportunity.id),
            title=opportunity.title,
            body=opportunity.body,
            tier=opportunity.tier,
            starts_at=(
                opportunity.event.starts_at
                if opportunity.event is not None
                else opportunity.expires_at
            ),
            walk_minutes=opportunity.walk_minutes or 12,
            travel_description=opportunity.travel_description or "Short walk",
            tags=opportunity.event.tags or [] if opportunity.event else [],
            source_url=opportunity.event.source_url if opportunity.event else None,
            cost_pence=opportunity.event.cost_pence or 0 if opportunity.event else 0,
            expected_attendees=(
                opportunity.event.attendee_count_estimate if opportunity.event else None
            ),
            social_proof_text=opportunity.social_proof_text,
        )
        for opportunity in opportunities
    ]

    state = ActivationState(
        user_id=current_user.id,
        current_time=now,
        comfort_level=current_user.comfort_level,
        activation_stage=current_user.activation_stage,
        willingness_radius_km=current_user.willingness_radius_km,
        user_preferences=[preference.category for preference in current_user.preferences],
        candidates=candidates,
    )
    result_state = run_activation_pipeline(state)
    if result_state.final_candidate is None:
        return None

    chosen_id = result_state.final_candidate.candidate_id
    return next(
        (opportunity for opportunity in opportunities if str(opportunity.id) == chosen_id),
        None,
    )


async def _get_or_create_fallback_opportunity(*, session: AsyncSession) -> Opportunity:
    now = datetime.now(UTC)
    result = await session.execute(
        select(Opportunity)
        .where(
            Opportunity.tier == OpportunityTier.SOLO_NUDGE,
            Opportunity.title == FALLBACK_OPPORTUNITY_TITLE,
            Opportunity.expires_at > now,
        )
        .order_by(Opportunity.expires_at.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    fallback = Opportunity(
        tier=OpportunityTier.SOLO_NUDGE,
        title=FALLBACK_OPPORTUNITY_TITLE,
        body="A 10-minute walk can reset your evening momentum.",
        walk_minutes=10,
        travel_description="10 min walk around your area",
        social_proof_text="No planning required",
        expires_at=now + timedelta(hours=24),
    )
    session.add(fallback)
    await session.flush()
    return fallback


def _fallback_coordinates(current_user: User) -> tuple[float, float]:
    return (
        current_user.location_lat if current_user.location_lat is not None else LONDON_FALLBACK_LAT,
        current_user.location_lng if current_user.location_lng is not None else LONDON_FALLBACK_LNG,
    )


@router.post("/check", response_model=ActivationCardResponse | NoOpportunityResponse)
async def check_activations(
    payload: ActivationCheckRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ActivationCardResponse | NoOpportunityResponse:
    location_updated = False
    if payload and payload.lat is not None and payload.lng is not None:
        current_user.location_lat = payload.lat
        current_user.location_lng = payload.lng
        current_user.location_updated_at = datetime.now(UTC)
        location_updated = True

    pending_activation = await _find_pending_activation(session=session, user_id=current_user.id)
    if pending_activation:
        if location_updated:
            await session.commit()
        fallback_lat, fallback_lng = _fallback_coordinates(current_user)
        venue_coordinates_cache: dict[UUID, tuple[float | None, float | None]] = {}
        mapped = await _to_opportunity_schema(
            session=session,
            opportunity=pending_activation.opportunity,
            fallback_lat=fallback_lat,
            fallback_lng=fallback_lng,
            venue_coordinates_cache=venue_coordinates_cache,
        )
        return ActivationCardResponse(
            activation_id=pending_activation.id,
            opportunity=mapped,
            stage=current_user.activation_stage,
            expires_at=pending_activation.opportunity.expires_at,
        )

    candidate = await _find_candidate_opportunity(session=session, current_user=current_user)
    if candidate is None:
        candidate = await _get_or_create_fallback_opportunity(session=session)

    activation = Activation(
        user_id=current_user.id,
        opportunity_id=candidate.id,
        shown_at=datetime.now(UTC),
    )
    session.add(activation)
    await session.commit()

    hydrated_activation = await _find_pending_activation(session=session, user_id=current_user.id)
    if hydrated_activation is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create activation.",
        )

    fallback_lat, fallback_lng = _fallback_coordinates(current_user)
    venue_coordinates_cache: dict[UUID, tuple[float | None, float | None]] = {}
    mapped = await _to_opportunity_schema(
        session=session,
        opportunity=hydrated_activation.opportunity,
        fallback_lat=fallback_lat,
        fallback_lng=fallback_lng,
        venue_coordinates_cache=venue_coordinates_cache,
    )
    return ActivationCardResponse(
        activation_id=hydrated_activation.id,
        opportunity=mapped,
        stage=current_user.activation_stage,
        expires_at=hydrated_activation.opportunity.expires_at,
    )


@router.get("/current", response_model=ActivationCardResponse | dict[str, None])
async def get_current_activation(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ActivationCardResponse | dict[str, None]:
    activation = await _find_pending_activation(session=session, user_id=current_user.id)
    if activation is None:
        return {"activation_id": None, "opportunity": None}

    fallback_lat, fallback_lng = _fallback_coordinates(current_user)
    venue_coordinates_cache: dict[UUID, tuple[float | None, float | None]] = {}
    mapped = await _to_opportunity_schema(
        session=session,
        opportunity=activation.opportunity,
        fallback_lat=fallback_lat,
        fallback_lng=fallback_lng,
        venue_coordinates_cache=venue_coordinates_cache,
    )
    return ActivationCardResponse(
        activation_id=activation.id,
        opportunity=mapped,
        stage=current_user.activation_stage,
        expires_at=activation.opportunity.expires_at,
    )


@router.post("/{id}/respond")
async def respond_to_activation(
    id: UUID,
    payload: ActivationRespondRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    result = await session.execute(
        select(Activation).where(
            Activation.id == id,
            Activation.user_id == current_user.id,
        )
    )
    activation = result.scalar_one_or_none()
    if activation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activation not found")

    activation.response = payload.response
    activation.responded_at = datetime.now(UTC)
    await session.commit()
    return {"status": "ok"}


@router.get("/history", response_model=ActivationHistoryResponse)
async def get_activation_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ActivationHistoryResponse:
    total = await session.scalar(
        select(func.count(Activation.id)).where(Activation.user_id == current_user.id)
    )
    result = await session.execute(
        select(Activation)
        .where(Activation.user_id == current_user.id)
        .order_by(Activation.shown_at.desc())
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Activation.opportunity)
            .selectinload(Opportunity.event)
            .selectinload(Event.venue)
        )
    )
    activations = result.scalars().all()

    fallback_lat, fallback_lng = _fallback_coordinates(current_user)
    venue_coordinates_cache: dict[UUID, tuple[float | None, float | None]] = {}
    items: list[ActivationHistoryItem] = []
    for activation in activations:
        mapped_opportunity = await _to_opportunity_schema(
            session=session,
            opportunity=activation.opportunity,
            fallback_lat=fallback_lat,
            fallback_lng=fallback_lng,
            venue_coordinates_cache=venue_coordinates_cache,
        )
        items.append(
            ActivationHistoryItem(
                id=activation.id,
                opportunity=mapped_opportunity,
                shown_at=activation.shown_at,
                response=activation.response,
                attended=activation.attended,
                rating=activation.rating,
                feedback_text=activation.feedback_text,
            )
        )

    return ActivationHistoryResponse(items=items, total=int(total or 0))
