from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

from scripts.seed_demo_social_proof import DEFAULT_USER_COUNT, build_and_write_demo_seed_data

from app.models.enums import ComfortLevel
from app.utils.llm import extract_tags_from_text

REPO_ROOT = Path(__file__).resolve().parents[3]
SEEDS_DIR = REPO_ROOT / "data" / "seeds"
USERS_PATH = SEEDS_DIR / "synthetic_users.json"


@dataclass(frozen=True)
class DemoAttendee:
    user_id: str
    display_name: str
    response: str
    solo: bool
    comfort_level: ComfortLevel
    cohort: str | None
    interests: list[str]


@dataclass(frozen=True)
class DemoAttendeePayload:
    event_key: str
    event_title: str
    total_expected: int
    solo_count: int
    attendees: list[DemoAttendee]


def _normalize_interest_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        value = tag.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


class DemoSocialGraphService:
    def __init__(self) -> None:
        self._users = self._load_users()

    def _load_users(self) -> list[dict[str, Any]]:
        if not USERS_PATH.exists():
            build_and_write_demo_seed_data(user_count=DEFAULT_USER_COUNT)

        try:
            payload = json.loads(USERS_PATH.read_text(encoding="utf-8"))
            users = [item for item in payload if isinstance(item, dict)]
        except (json.JSONDecodeError, OSError):
            users = []

        if len(users) < DEFAULT_USER_COUNT:
            build_and_write_demo_seed_data(user_count=DEFAULT_USER_COUNT)
            payload = json.loads(USERS_PATH.read_text(encoding="utf-8"))
            users = [item for item in payload if isinstance(item, dict)]
        return users

    def _event_categories(self, *, event_title: str, event_tags: list[str]) -> list[str]:
        inferred = extract_tags_from_text(event_title, limit=6)
        return _normalize_interest_tags(event_tags + inferred)

    def _user_interest_scores(
        self,
        *,
        event_key: str,
        categories: list[str],
    ) -> list[tuple[dict[str, Any], float]]:
        scored: list[tuple[dict[str, Any], float]] = []
        for user in self._users:
            preferences = user.get("preferences", [])
            pref_map: dict[str, float] = {}
            for pref in preferences:
                category = str(pref.get("category", "")).strip().lower()
                if not category:
                    continue
                weight = float(pref.get("weight", 0.5))
                pref_map[category] = weight

            overlap = [category for category in categories if category in pref_map]
            overlap_score = sum(pref_map.get(category, 0.0) for category in overlap)
            overlap_boost = 0.45 if overlap else 0.0
            stable_noise = self._stable_user_noise(
                event_key=event_key,
                user_id=str(user.get("user_id", "")),
            )
            score = overlap_score + overlap_boost + stable_noise
            scored.append((user, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored

    def _stable_user_noise(self, *, event_key: str, user_id: str) -> float:
        digest = hashlib.sha256(f"{event_key}:{user_id}".encode("utf-8")).hexdigest()
        return (int(digest[:6], 16) % 100) / 1000.0

    def _interest_list(self, user: dict[str, Any]) -> list[str]:
        preferences = user.get("preferences", [])
        weighted: list[tuple[str, float]] = []
        for pref in preferences:
            category = str(pref.get("category", "")).strip().lower()
            if not category:
                continue
            weighted.append((category, float(pref.get("weight", 0.5))))
        weighted.sort(key=lambda item: item[1], reverse=True)
        return [category for category, _ in weighted[:3]]

    def _solo_probability(self, comfort_level: ComfortLevel) -> float:
        if comfort_level is ComfortLevel.SOLO_OK:
            return 0.72
        if comfort_level is ComfortLevel.PREFER_OTHERS:
            return 0.42
        return 0.16

    def build_attendees_for_event(
        self,
        *,
        event_key: str,
        event_title: str,
        event_tags: list[str],
        attendee_hint: int | None = None,
    ) -> DemoAttendeePayload:
        categories = self._event_categories(event_title=event_title, event_tags=event_tags)
        scored_users = self._user_interest_scores(event_key=event_key, categories=categories)

        seed_int = int(hashlib.sha256(event_key.encode("utf-8")).hexdigest()[:8], 16)
        rng = Random(seed_int)
        default_hint = 14 + min(len(categories), 4) * 3
        target_size = max(10, min(36, attendee_hint or default_hint))
        pool_size = min(len(scored_users), target_size * 4)
        pool = scored_users[:pool_size]

        attendees: list[DemoAttendee] = []
        selected_indices: set[int] = set()
        while len(attendees) < target_size and len(selected_indices) < len(pool):
            weights = [max(0.01, score) for _, score in pool]
            picked = rng.choices(range(len(pool)), weights=weights, k=1)[0]
            if picked in selected_indices:
                continue
            selected_indices.add(picked)

            user, score = pool[picked]
            comfort = ComfortLevel(str(user.get("comfort_level", ComfortLevel.SOLO_OK.value)))
            response_probability = 0.8 if score >= 1.0 else 0.7
            response = "going" if rng.random() < response_probability else "interested"
            solo = response == "going" and rng.random() < self._solo_probability(comfort)
            attendees.append(
                DemoAttendee(
                    user_id=str(user.get("user_id", "")),
                    display_name=str(user.get("display_name", "Demo User")),
                    response=response,
                    solo=solo,
                    comfort_level=comfort,
                    cohort=str(user.get("cohort")) if user.get("cohort") else None,
                    interests=self._interest_list(user),
                )
            )

        attendees.sort(key=lambda attendee: (attendee.response != "going", not attendee.solo))
        going = [attendee for attendee in attendees if attendee.response == "going"]
        total_expected = len(going)
        solo_count = sum(1 for attendee in going if attendee.solo)
        return DemoAttendeePayload(
            event_key=event_key,
            event_title=event_title,
            total_expected=total_expected,
            solo_count=solo_count,
            attendees=attendees,
        )
