from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from random import Random
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "seeds"
DEFAULT_USER_COUNT = 300
DEFAULT_SEED = 20260315

COHORTS = [
    {
        "id": "bloomsbury_students",
        "zone": "bloomsbury",
        "center": {"lat": 51.5235, "lng": -0.1259},
        "comfort_weights": [("solo_ok", 0.35), ("prefer_others", 0.4), ("need_familiar", 0.25)],
        "stage_weights": [("suggest", 0.55), ("recommend", 0.35), ("precommit", 0.1)],
        "radius_range": (1.2, 4.2),
        "preferences": ["study", "art", "music", "food", "community", "outdoors"],
        "persona_templates": [
            "studying for finals and looking for low-cost evening plans",
            "new in London and trying to build a familiar routine",
            "balancing coursework with creative activities after lectures",
        ],
    },
    {
        "id": "shoreditch_remote_workers",
        "zone": "shoreditch",
        "center": {"lat": 51.5247, "lng": -0.0794},
        "comfort_weights": [("solo_ok", 0.5), ("prefer_others", 0.35), ("need_familiar", 0.15)],
        "stage_weights": [("suggest", 0.35), ("recommend", 0.45), ("precommit", 0.2)],
        "radius_range": (1.8, 6.5),
        "preferences": ["food", "music", "fitness", "tech", "community", "art"],
        "persona_templates": [
            "finishing remote work and needing a post-work reset",
            "seeking social events after long days of solo focus",
            "open to one-tap plans if travel time stays under 20 minutes",
        ],
    },
    {
        "id": "weekend_park_goers",
        "zone": "parks",
        "center": {"lat": 51.5368, "lng": -0.0469},
        "comfort_weights": [("solo_ok", 0.42), ("prefer_others", 0.33), ("need_familiar", 0.25)],
        "stage_weights": [("suggest", 0.45), ("recommend", 0.4), ("precommit", 0.15)],
        "radius_range": (1.4, 5.4),
        "preferences": ["outdoors", "fitness", "food", "community", "music", "wellness"],
        "persona_templates": [
            "active on weekends but inconsistent about committing",
            "likes park-based activities with low social pressure",
            "wants casual group plans without heavy logistics",
        ],
    },
]

FIRST_NAMES = [
    "Ava",
    "Noah",
    "Mia",
    "Luca",
    "Zara",
    "Leo",
    "Nora",
    "Hugo",
    "Ivy",
    "Aria",
    "Omar",
    "Elena",
    "Ethan",
    "Layla",
    "Theo",
    "Mila",
    "Adam",
    "Sana",
    "Kai",
    "Freya",
]
LAST_NAMES = [
    "Patel",
    "Khan",
    "Sharma",
    "Ali",
    "Smith",
    "Taylor",
    "Baker",
    "Hughes",
    "Singh",
    "Reed",
    "Morris",
    "Evans",
    "Lopez",
    "Walker",
    "Nguyen",
    "Wright",
    "Ross",
    "Ahmed",
    "Ward",
    "Foster",
]

DEMO_OPPORTUNITIES = [
    {
        "opportunity_id": "demo-opp-001",
        "title": "Life Drawing at The Art House",
        "scenario": "post_work_drift",
        "zone": "shoreditch",
        "tier": "structured",
        "starts_at": "2026-03-18T18:30:00Z",
        "target_cohorts": ["shoreditch_remote_workers", "bloomsbury_students"],
    },
    {
        "opportunity_id": "demo-opp-002",
        "title": "Canal Walk + Coffee Meetup",
        "scenario": "post_work_drift",
        "zone": "shoreditch",
        "tier": "recurring_pattern",
        "starts_at": "2026-03-18T18:15:00Z",
        "target_cohorts": ["shoreditch_remote_workers"],
    },
    {
        "opportunity_id": "demo-opp-003",
        "title": "Beginner Bouldering Social",
        "scenario": "post_work_drift",
        "zone": "shoreditch",
        "tier": "structured",
        "starts_at": "2026-03-19T19:00:00Z",
        "target_cohorts": ["shoreditch_remote_workers", "bloomsbury_students"],
    },
    {
        "opportunity_id": "demo-opp-004",
        "title": "Victoria Park Morning Run",
        "scenario": "weekend_morning_void",
        "zone": "parks",
        "tier": "recurring_pattern",
        "starts_at": "2026-03-21T09:30:00Z",
        "target_cohorts": ["weekend_park_goers", "shoreditch_remote_workers"],
    },
    {
        "opportunity_id": "demo-opp-005",
        "title": "Columbia Road Flower Walk",
        "scenario": "weekend_morning_void",
        "zone": "shoreditch",
        "tier": "structured",
        "starts_at": "2026-03-21T10:15:00Z",
        "target_cohorts": ["weekend_park_goers", "bloomsbury_students"],
    },
    {
        "opportunity_id": "demo-opp-006",
        "title": "Lakeside Sketch Session",
        "scenario": "weekend_morning_void",
        "zone": "parks",
        "tier": "solo_nudge",
        "starts_at": "2026-03-22T10:00:00Z",
        "target_cohorts": ["weekend_park_goers", "bloomsbury_students"],
    },
    {
        "opportunity_id": "demo-opp-007",
        "title": "Last-Minute Ramen Group",
        "scenario": "cancelled_plan_gap",
        "zone": "shoreditch",
        "tier": "micro_coordination",
        "starts_at": "2026-03-20T19:10:00Z",
        "target_cohorts": ["shoreditch_remote_workers", "weekend_park_goers"],
    },
    {
        "opportunity_id": "demo-opp-008",
        "title": "Drop-In Co-Study at Senate House",
        "scenario": "cancelled_plan_gap",
        "zone": "bloomsbury",
        "tier": "micro_coordination",
        "starts_at": "2026-03-20T18:45:00Z",
        "target_cohorts": ["bloomsbury_students"],
    },
    {
        "opportunity_id": "demo-opp-009",
        "title": "Open Mic Backup Plan",
        "scenario": "cancelled_plan_gap",
        "zone": "shoreditch",
        "tier": "structured",
        "starts_at": "2026-03-20T20:00:00Z",
        "target_cohorts": ["shoreditch_remote_workers", "bloomsbury_students"],
    },
]


def _split_counts(total: int, partitions: int) -> list[int]:
    base = total // partitions
    remainder = total % partitions
    return [base + (1 if index < remainder else 0) for index in range(partitions)]


def _weighted_choice(rng: Random, weighted_values: list[tuple[str, float]]) -> str:
    options = [value for value, _ in weighted_values]
    weights = [weight for _, weight in weighted_values]
    return rng.choices(options, weights=weights, k=1)[0]


def _build_preferences(rng: Random, available_categories: list[str]) -> list[dict[str, Any]]:
    selected_categories = rng.sample(available_categories, k=3)
    preferences: list[dict[str, Any]] = []
    for category in selected_categories:
        preferences.append(
            {
                "category": category,
                "weight": round(rng.uniform(0.45, 0.95), 2),
                "explicit": bool(rng.random() >= 0.2),
            }
        )
    return preferences


def _jitter_location(rng: Random, lat: float, lng: float) -> dict[str, float]:
    return {
        "lat": round(lat + rng.uniform(-0.015, 0.015), 6),
        "lng": round(lng + rng.uniform(-0.02, 0.02), 6),
    }


def generate_demo_users(
    user_count: int = DEFAULT_USER_COUNT,
    seed: int = DEFAULT_SEED,
) -> list[dict[str, Any]]:
    rng = Random(seed)
    users: list[dict[str, Any]] = []
    cohort_counts = _split_counts(user_count, len(COHORTS))

    user_index = 1
    for cohort, cohort_count in zip(COHORTS, cohort_counts, strict=True):
        for local_index in range(cohort_count):
            first_name = FIRST_NAMES[(user_index - 1) % len(FIRST_NAMES)]
            last_name = LAST_NAMES[((user_index - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)]
            display_name = f"{first_name} {last_name}"
            profile_location = _jitter_location(
                rng,
                cohort["center"]["lat"],
                cohort["center"]["lng"],
            )

            comfort_level = _weighted_choice(rng, cohort["comfort_weights"])
            activation_stage = _weighted_choice(rng, cohort["stage_weights"])
            willingness_radius = round(
                rng.uniform(cohort["radius_range"][0], cohort["radius_range"][1]),
                2,
            )
            preferences = _build_preferences(rng, cohort["preferences"])
            persona_summary = rng.choice(cohort["persona_templates"])

            users.append(
                {
                    "user_id": f"demo-user-{user_index:04d}",
                    "email": f"demo.user.{user_index:04d}@firstmove.demo",
                    "display_name": display_name,
                    "cohort": cohort["id"],
                    "home_zone": cohort["zone"],
                    "location": profile_location,
                    "timezone": "Europe/London",
                    "comfort_level": comfort_level,
                    "activation_stage": activation_stage,
                    "willingness_radius_km": willingness_radius,
                    "preferences": preferences,
                    "familiar_cluster": f"{cohort['id']}-cluster-{(local_index // 10) + 1:02d}",
                    "persona_summary": persona_summary,
                }
            )
            user_index += 1

    return users


def generate_demo_activity(users: list[dict[str, Any]], seed: int = DEFAULT_SEED) -> dict[str, Any]:
    rng = Random(seed + 101)
    users_by_cohort: dict[str, list[dict[str, Any]]] = {}
    for user in users:
        users_by_cohort.setdefault(user["cohort"], []).append(user)

    opportunities: list[dict[str, Any]] = []
    for template in DEMO_OPPORTUNITIES:
        candidate_users: list[dict[str, Any]] = []
        for cohort in template["target_cohorts"]:
            candidate_users.extend(users_by_cohort.get(cohort, []))

        attendee_target = min(len(candidate_users), rng.randint(14, 36))
        selected_users = rng.sample(candidate_users, k=attendee_target)

        attendees: list[dict[str, Any]] = []
        for user in selected_users:
            response = "going" if rng.random() < 0.82 else "interested"
            solo_probability = {
                "solo_ok": 0.72,
                "prefer_others": 0.44,
                "need_familiar": 0.18,
            }[user["comfort_level"]]
            solo = response == "going" and rng.random() < solo_probability
            attendees.append(
                {
                    "user_id": user["user_id"],
                    "display_name": user["display_name"],
                    "cohort": user["cohort"],
                    "response": response,
                    "solo": solo,
                    "familiar_cluster": user["familiar_cluster"],
                }
            )

        going_attendees = [attendee for attendee in attendees if attendee["response"] == "going"]
        cluster_counts = Counter(
            attendee["familiar_cluster"] for attendee in going_attendees if not attendee["solo"]
        )
        top_clusters = [
            {"cluster_id": cluster_id, "count": count}
            for cluster_id, count in cluster_counts.most_common(3)
        ]
        social_proof_snapshot = {
            "total_expected": len(going_attendees),
            "solo_count": sum(1 for attendee in going_attendees if attendee["solo"]),
            "familiar_cluster_count": sum(1 for count in cluster_counts.values() if count >= 2),
            "top_familiar_clusters": top_clusters,
        }

        opportunities.append(
            {
                "opportunity_id": template["opportunity_id"],
                "title": template["title"],
                "scenario": template["scenario"],
                "zone": template["zone"],
                "tier": template["tier"],
                "starts_at": template["starts_at"],
                "social_proof_snapshot": social_proof_snapshot,
                "attendees": attendees,
            }
        )

    scenario_example = {}
    for opportunity in opportunities:
        scenario_example.setdefault(opportunity["scenario"], opportunity)

    walkthrough: list[dict[str, Any]] = []
    step = 1
    for scenario in ("post_work_drift", "weekend_morning_void", "cancelled_plan_gap"):
        opportunity = scenario_example[scenario]
        candidate_user = next(
            (
                user
                for user in users
                if user["cohort"] in next(
                    item["target_cohorts"]
                    for item in DEMO_OPPORTUNITIES
                    if item["opportunity_id"] == opportunity["opportunity_id"]
                )
            ),
            users[0],
        )
        snapshot = opportunity["social_proof_snapshot"]
        walkthrough.append(
            {
                "step": step,
                "scenario": scenario,
                "request_user_id": candidate_user["user_id"],
                "request_user_display_name": candidate_user["display_name"],
                "opportunity_id": opportunity["opportunity_id"],
                "expected_social_proof": (
                    f"{snapshot['total_expected']} people likely going, "
                    f"{snapshot['solo_count']} going solo"
                ),
            }
        )
        step += 1

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "seed": seed,
        "opportunities": opportunities,
        "demo_walkthrough": walkthrough,
    }


def write_demo_seed_files(
    users: list[dict[str, Any]],
    activity: dict[str, Any],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    user_file = output_dir / "synthetic_users.json"
    activity_file = output_dir / "synthetic_user_activity.json"

    user_file.write_text(json.dumps(users, indent=2), encoding="utf-8")
    activity_file.write_text(json.dumps(activity, indent=2), encoding="utf-8")
    return {"users": user_file, "activity": activity_file}


def build_and_write_demo_seed_data(
    user_count: int = DEFAULT_USER_COUNT,
    seed: int = DEFAULT_SEED,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    users = generate_demo_users(user_count=user_count, seed=seed)
    activity = generate_demo_activity(users=users, seed=seed)
    paths = write_demo_seed_files(users=users, activity=activity, output_dir=output_dir)
    return {"users": users, "activity": activity, "paths": paths}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic social-proof demo data. "
            "Outputs synthetic_users.json and synthetic_user_activity.json."
        )
    )
    parser.add_argument(
        "--users",
        type=int,
        default=DEFAULT_USER_COUNT,
        help="Total synthetic users to generate (default: 300).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Deterministic random seed.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for seed files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_and_write_demo_seed_data(
        user_count=args.users,
        seed=args.seed,
        output_dir=args.output_dir,
    )
    print(
        json.dumps(
            {
                "users_generated": len(result["users"]),
                "opportunities_generated": len(result["activity"]["opportunities"]),
                "output_files": {
                    "users": str(result["paths"]["users"]),
                    "activity": str(result["paths"]["activity"]),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
