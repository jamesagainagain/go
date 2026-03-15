# FirstMove API - Unified Specification

**Source of truth:** `docs/api-spec.yaml` (OpenAPI 3.0)

Both frontend and backend must implement against this spec. No ad-hoc endpoints.

---

## Base URL

All endpoints are under `/api/v1`. Example: `POST /api/v1/auth/register`

## Authentication

Protected endpoints require: `Authorization: Bearer <jwt_token>`

---

## Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Create account (email + preferences) |
| POST | `/auth/login` | JWT login |
| GET | `/users/me` | Get profile + preferences |
| PATCH | `/users/me` | Update preferences, location, comfort level |
| POST | `/users/me/location` | Update real-time location |
| POST | `/activations/check` | Trigger activation check → opportunity or null |
| GET | `/activations/current` | Get current pending activation |
| POST | `/activations/{id}/respond` | Accept, dismiss, snooze |
| POST | `/activations/{id}/feedback` | Post-attendance feedback |
| GET | `/activations/history` | Past activations with outcomes |
| GET | `/events/nearby` | Browse events near location (fallback) |
| POST | `/push/subscribe` | Register Web Push subscription |
| POST | `/webhooks/calendar` | Google Calendar change notification |

---

## Key Response: Activation Card

When `POST /activations/check` finds an opportunity:

```json
{
  "activation_id": "uuid",
  "opportunity": {
    "title": "Life drawing at The Art House",
    "body": "Free drop-in session, all materials provided...",
    "tier": "structured",
    "walk_minutes": 9,
    "travel_description": "9 min walk along Regent's Canal",
    "starts_at": "2026-03-15T18:30:00Z",
    "leave_by": "2026-03-15T18:20:00Z",
    "cost_pence": 0,
    "venue": { "name": "The Art House", "lat": 51.534, "lng": -0.097 },
    "social_proof": {
      "text": "4 others going solo",
      "total_expected": 12,
      "solo_count": 4,
      "familiar_face": false
    },
    "commitment_action": {
      "type": "one_tap_rsvp",
      "label": "Hold my spot"
    },
    "route_polyline": "encoded_polyline_string"
  },
  "stage": "recommend",
  "expires_at": "2026-03-15T18:15:00Z"
}
```

---

## Enums

**ComfortLevel:** `solo_ok` | `prefer_others` | `need_familiar`  
**ActivationStage:** `suggest` | `recommend` | `precommit` | `activate`  
**ActivationResponse:** `accepted` | `dismissed` | `expired` | `snoozed`  
**OpportunityTier:** `structured` | `recurring_pattern` | `micro_coordination` | `solo_nudge`  
**CommitmentActionType:** `one_tap_rsvp` | `deep_link` | `internal_going` | `none`

---

## Usage

- **Backend:** Implement routes to match `api-spec.yaml`; use for validation and OpenAPI docs
- **Frontend:** Generate client from spec (e.g. `openapi-typescript`) or reference for fetch calls
