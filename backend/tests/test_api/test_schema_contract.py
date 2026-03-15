from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.main import app
from app.schemas.activation import ActivationCardResponse, NoOpportunityResponse
from app.schemas.user import RegisterRequest


def test_activation_card_response_serializes_valid_payload():
    payload = {
        "activation_id": str(uuid4()),
        "opportunity": {
            "title": "Life drawing at The Art House",
            "body": "Drop-in session with materials provided.",
            "tier": "structured",
            "walk_minutes": 9,
            "travel_description": "9 min walk",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "leave_by": datetime.now(timezone.utc).isoformat(),
            "cost_pence": 0,
            "venue": {"name": "The Art House", "lat": 51.534, "lng": -0.097},
        },
        "stage": "recommend",
        "expires_at": datetime.now(timezone.utc).isoformat(),
    }

    result = ActivationCardResponse.model_validate(payload)
    assert result.opportunity.title == payload["opportunity"]["title"]
    assert result.stage == "recommend"


def test_no_opportunity_response_accepts_null_fields():
    result = NoOpportunityResponse.model_validate(
        {
            "activation_id": None,
            "opportunity": None,
            "message": "No suitable opportunity right now",
        }
    )
    assert result.activation_id is None
    assert result.opportunity is None


def test_register_request_requires_email():
    with pytest.raises(ValidationError):
        RegisterRequest.model_validate({"password": "secret1234"})


def test_register_request_requires_password():
    with pytest.raises(ValidationError):
        RegisterRequest.model_validate({"email": "demo@example.com"})


def test_openapi_register_request_requires_password():
    required_fields = app.openapi()["components"]["schemas"]["RegisterRequest"]["required"]
    assert "password" in required_fields
