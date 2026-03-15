from datetime import datetime, timezone
from pathlib import Path
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


def test_openapi_includes_required_v1_routes():
    paths = app.openapi()["paths"]
    required_paths = {
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/users/me",
        "/api/v1/users/me/location",
        "/api/v1/activations/check",
        "/api/v1/activations/current",
        "/api/v1/activations/{id}/respond",
        "/api/v1/activations/{id}/feedback",
        "/api/v1/activations/history",
        "/api/v1/events/nearby",
        "/api/v1/push/subscribe",
        "/api/v1/webhooks/calendar",
    }
    assert required_paths.issubset(set(paths.keys()))


def test_api_spec_register_request_requires_password():
    spec_path = Path(__file__).resolve().parents[3] / "docs" / "api-spec.yaml"
    spec_text = spec_path.read_text(encoding="utf-8")
    register_block = spec_text.split("RegisterRequest:", maxsplit=1)[1]
    register_block = register_block.split("LoginRequest:", maxsplit=1)[0]
    assert "required: [email, password]" in register_block
