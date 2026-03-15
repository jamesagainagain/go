from __future__ import annotations

import pytest

from app.services.openclaw_profile_loop import _normalize_interest_tags


@pytest.mark.services
def test_normalize_interest_tags_dedupes_and_lowercases():
    tags = _normalize_interest_tags([" Art ", "MUSIC", "music", "", "community"])
    assert tags == ["art", "music", "community"]


@pytest.mark.services
def test_normalize_interest_tags_returns_empty_when_no_valid_tags():
    tags = _normalize_interest_tags(["", "   "])
    assert tags == []
