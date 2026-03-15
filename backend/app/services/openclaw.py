from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

import httpx

DEFAULT_OPENAI_CHAT_COMPLETIONS_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENCLAW_MODEL = "gpt-4o-mini"


@dataclass(slots=True)
class OpenClawSuggestion:
    title: str
    description: str | None
    starts_at: datetime
    location_text: str | None
    lat: float | None
    lng: float | None
    category: str
    source_url: str | None = None
    cost_hint: str | None = None
    tags: list[str] | None = None


class OpenClawProvider(Protocol):
    async def fetch_suggestions(
        self,
        *,
        city: str,
        hours_ahead: int,
    ) -> list[OpenClawSuggestion]:
        ...


class DisabledOpenClawProvider:
    async def fetch_suggestions(
        self,
        *,
        city: str,
        hours_ahead: int,
    ) -> list[OpenClawSuggestion]:
        del city, hours_ahead
        return []


class HttpOpenClawProvider:
    def __init__(
        self,
        *,
        endpoint: str,
        api_token: str,
        timeout_seconds: float = 4.0,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_token = api_token
        self._timeout_seconds = timeout_seconds

    async def fetch_suggestions(
        self,
        *,
        city: str,
        hours_ahead: int,
    ) -> list[OpenClawSuggestion]:
        payload = await self._fetch_payload(city=city, hours_ahead=hours_ahead)
        suggestions: list[OpenClawSuggestion] = []
        for item in payload:
            parsed = _parse_suggestion(item)
            if parsed is not None:
                suggestions.append(parsed)
        return suggestions

    async def _fetch_payload(self, *, city: str, hours_ahead: int) -> list[dict]:
        # Framework-only seam: returns [] on any shape/network/auth issue.
        # This keeps OpenClaw disabled-by-default and non-blocking for demo runtime.
        timeout = httpx.Timeout(self._timeout_seconds)
        headers = {"Authorization": f"Bearer {self._api_token}"}
        params = {"city": city, "hours_ahead": str(hours_ahead)}
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(self._endpoint, headers=headers, params=params)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return []

        if not isinstance(payload, list):
            return []
        return [item for item in payload if isinstance(item, dict)]


class OpenAIChatCompletionsOpenClawProvider:
    def __init__(
        self,
        *,
        endpoint: str | None,
        api_token: str,
        timeout_seconds: float = 4.0,
        model: str = DEFAULT_OPENCLAW_MODEL,
    ) -> None:
        self._endpoint = _normalize_openai_endpoint(endpoint)
        self._api_token = api_token
        self._timeout_seconds = timeout_seconds
        self._model = model

    async def fetch_suggestions(
        self,
        *,
        city: str,
        hours_ahead: int,
    ) -> list[OpenClawSuggestion]:
        payload = await self._fetch_payload(city=city, hours_ahead=hours_ahead)
        suggestions: list[OpenClawSuggestion] = []
        for item in payload:
            parsed = _parse_suggestion(item)
            if parsed is not None:
                suggestions.append(parsed)
        return suggestions

    async def _fetch_payload(self, *, city: str, hours_ahead: int) -> list[dict]:
        timeout = httpx.Timeout(self._timeout_seconds)
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self._model,
            "temperature": 0.2,
            "max_tokens": 500,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are OpenClaw for FirstMove. Return JSON only with key "
                        "'suggestions', containing 3-8 nearby opportunities. "
                        "Each suggestion item must contain: "
                        "title, description, starts_at (ISO8601), location_text, lat, lng, "
                        "category, source_url, cost_hint, tags."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"City: {city}\n"
                        f"Time window: next {hours_ahead} hours.\n"
                        "Focus on low-friction social, cultural, fitness, food, and community options."
                    ),
                },
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self._endpoint, headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return []

        content = _extract_openai_chat_content(payload)
        if not content:
            return []
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return []

        suggestions = parsed.get("suggestions", parsed if isinstance(parsed, list) else [])
        if not isinstance(suggestions, list):
            return []
        return [item for item in suggestions if isinstance(item, dict)]


def build_openclaw_provider(
    *,
    enabled: bool,
    endpoint: str | None,
    api_token: str | None,
    timeout_seconds: float = 4.0,
    model: str = DEFAULT_OPENCLAW_MODEL,
) -> OpenClawProvider:
    if not enabled or not api_token:
        return DisabledOpenClawProvider()
    if _is_openai_endpoint(endpoint):
        return OpenAIChatCompletionsOpenClawProvider(
            endpoint=endpoint,
            api_token=api_token,
            timeout_seconds=timeout_seconds,
            model=model,
        )
    if not endpoint:
        return DisabledOpenClawProvider()
    return HttpOpenClawProvider(
        endpoint=endpoint,
        api_token=api_token,
        timeout_seconds=timeout_seconds,
    )


def _parse_suggestion(payload: dict) -> OpenClawSuggestion | None:
    title = _coerce_text(payload.get("title"))
    if not title:
        return None

    starts_at = _coerce_datetime(payload.get("starts_at"))
    if starts_at is None:
        return None

    category = _coerce_text(payload.get("category")) or "micro_coordination"
    return OpenClawSuggestion(
        title=title,
        description=_coerce_text(payload.get("description")),
        starts_at=starts_at,
        location_text=_coerce_text(payload.get("location_text")),
        lat=_coerce_float(payload.get("lat")),
        lng=_coerce_float(payload.get("lng")),
        category=category,
        source_url=_coerce_text(payload.get("source_url")),
        cost_hint=_coerce_text(payload.get("cost_hint")),
        tags=_coerce_tags(payload.get("tags")),
    )


def _coerce_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return _ensure_utc(value)
    text = _coerce_text(value)
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        return _ensure_utc(datetime.fromisoformat(normalized))
    except ValueError:
        return None


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _coerce_tags(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    tags: list[str] = []
    for item in value:
        text = _coerce_text(item)
        if text:
            tags.append(text.lower())
    return tags or None


def build_placeholder_suggestions(*, city: str, hours_ahead: int) -> list[OpenClawSuggestion]:
    if city.strip().lower() != "london":
        return []
    now = datetime.now(UTC).replace(second=0, microsecond=0)
    starts_at = now + timedelta(hours=max(1, min(hours_ahead, 6)))
    return [
        OpenClawSuggestion(
            title="OpenClaw placeholder suggestion",
            description="Framework-only placeholder while OpenClaw integration is deferred.",
            starts_at=starts_at,
            location_text="London",
            lat=51.5074,
            lng=-0.1278,
            category="micro_coordination",
            tags=["openclaw", "placeholder"],
        )
    ]


def _extract_openai_chat_content(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None
    message = first.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
        if text_parts:
            return "".join(text_parts)
    return None


def _is_openai_endpoint(endpoint: str | None) -> bool:
    if endpoint is None:
        return True
    normalized = endpoint.strip().lower()
    return "api.openai.com" in normalized


def _normalize_openai_endpoint(endpoint: str | None) -> str:
    if not endpoint:
        return DEFAULT_OPENAI_CHAT_COMPLETIONS_ENDPOINT
    value = endpoint.rstrip("/")
    if "/v1/" in value:
        return value
    if value.endswith("/v1/chat/completions"):
        return value
    if value.endswith("/v1"):
        return f"{value}/chat/completions"
    if value.startswith("https://api.openai.com"):
        return f"{value}/v1/chat/completions"
    return value
