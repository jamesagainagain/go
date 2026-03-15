from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models import Activation, Opportunity, User
from app.schemas.activation import FeedbackRequest
from app.services.post_event_profile import process_post_event_feedback
from app.utils.security import get_current_user

router = APIRouter(prefix="/activations", tags=["activations"])


@router.post("/{id}/feedback")
async def post_feedback(
    id: UUID,
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    result = await session.execute(
        select(Activation)
        .where(
            Activation.id == id,
            Activation.user_id == current_user.id,
        )
        .options(selectinload(Activation.opportunity).selectinload(Opportunity.event))
    )
    activation = result.scalar_one_or_none()
    if activation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activation not found")

    activation.attended = payload.attended
    activation.rating = payload.rating
    activation.feedback_text = payload.feedback_text
    if activation.responded_at is None:
        activation.responded_at = datetime.now(UTC)

    review_reason = await process_post_event_feedback(
        session=session,
        user=current_user,
        activation=activation,
        attended=payload.attended,
        rating=payload.rating,
        feedback_text=payload.feedback_text,
    )

    await session.commit()
    return {"status": "ok", "review": review_reason}
