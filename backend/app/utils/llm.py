from __future__ import annotations

from app.config import get_settings

KEYWORD_TAGS: dict[str, tuple[str, ...]] = {
    "art": ("art", "gallery", "drawing", "painting", "sketch"),
    "music": ("music", "open mic", "gig", "concert", "dj"),
    "fitness": ("run", "running", "yoga", "gym", "workout", "climb", "boulder"),
    "community": ("meetup", "community", "social", "friends", "network"),
    "food": ("food", "dinner", "ramen", "brunch", "coffee", "cafe"),
    "study": ("study", "co-study", "lecture", "workshop", "book club"),
    "outdoors": ("park", "walk", "outdoor", "canal", "market"),
}


def build_openai_metadata() -> dict[str, str | None]:
    settings = get_settings()
    return {
        "model": settings.openai_model_fast,
        "api_key_present": "yes" if settings.openai_api_key else "no",
    }


def extract_tags_from_text(text: str, *, limit: int = 5) -> list[str]:
    lowered = text.lower()
    tags = [
        tag
        for tag, keywords in KEYWORD_TAGS.items()
        if any(word in lowered for word in keywords)
    ]
    if not tags:
        return ["community"]
    return tags[:limit]


def estimate_solo_friendly_score(text: str) -> float:
    lowered = text.lower()
    score = 0.45
    positive_signals = ("drop-in", "beginner", "solo", "friendly", "casual", "all welcome")
    for signal in positive_signals:
        if signal in lowered:
            score += 0.08
    if "members only" in lowered or "invite only" in lowered:
        score -= 0.2
    return max(0.0, min(1.0, score))
