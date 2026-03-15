from __future__ import annotations

import json
from collections import Counter

from scripts.seed_demo_social_proof import (
    build_and_write_demo_seed_data,
    generate_demo_activity,
    generate_demo_users,
)


def test_generate_demo_users_count_and_distribution():
    users = generate_demo_users(user_count=300, seed=7)

    assert len(users) == 300
    assert len({user["user_id"] for user in users}) == 300
    assert len({user["email"] for user in users}) == 300

    cohort_counts = Counter(user["cohort"] for user in users)
    assert cohort_counts == {
        "bloomsbury_students": 100,
        "shoreditch_remote_workers": 100,
        "weekend_park_goers": 100,
    }
    assert {user["comfort_level"] for user in users} == {
        "solo_ok",
        "prefer_others",
        "need_familiar",
    }


def test_generate_demo_activity_supports_demo_scenarios():
    users = generate_demo_users(user_count=300, seed=7)
    activity = generate_demo_activity(users=users, seed=7)

    scenarios = {opportunity["scenario"] for opportunity in activity["opportunities"]}
    assert {"post_work_drift", "weekend_morning_void", "cancelled_plan_gap"}.issubset(scenarios)

    for opportunity in activity["opportunities"]:
        snapshot = opportunity["social_proof_snapshot"]
        assert snapshot["total_expected"] >= snapshot["solo_count"]
        assert snapshot["total_expected"] > 0

    assert len(activity["demo_walkthrough"]) == 3


def test_demo_seed_generation_is_deterministic():
    users_a = generate_demo_users(user_count=300, seed=11)
    users_b = generate_demo_users(user_count=300, seed=11)
    assert users_a == users_b

    activity_a = generate_demo_activity(users=users_a, seed=11)
    activity_b = generate_demo_activity(users=users_b, seed=11)
    assert activity_a["opportunities"] == activity_b["opportunities"]
    assert activity_a["demo_walkthrough"] == activity_b["demo_walkthrough"]


def test_write_demo_seed_files(tmp_path):
    result = build_and_write_demo_seed_data(user_count=300, seed=13, output_dir=tmp_path)
    users_path = result["paths"]["users"]
    activity_path = result["paths"]["activity"]

    assert users_path.exists()
    assert activity_path.exists()

    users = json.loads(users_path.read_text(encoding="utf-8"))
    activity = json.loads(activity_path.read_text(encoding="utf-8"))
    assert len(users) == 300
    assert len(activity["opportunities"]) >= 9
