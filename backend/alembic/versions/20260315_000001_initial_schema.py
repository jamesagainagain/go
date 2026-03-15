"""initial schema

Revision ID: 20260315_000001
Revises:
Create Date: 2026-03-15 00:00:01.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260315_000001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    comfort_level_enum = postgresql.ENUM(
        "solo_ok",
        "prefer_others",
        "need_familiar",
        name="comfort_level",
    )
    activation_stage_enum = postgresql.ENUM(
        "suggest",
        "recommend",
        "precommit",
        "activate",
        name="activation_stage",
    )
    opportunity_tier_enum = postgresql.ENUM(
        "structured",
        "recurring_pattern",
        "micro_coordination",
        "solo_nudge",
        name="opportunity_tier",
    )
    activation_response_enum = postgresql.ENUM(
        "accepted",
        "dismissed",
        "expired",
        "snoozed",
        name="activation_response",
    )

    comfort_level_enum.create(op.get_bind(), checkfirst=True)
    activation_stage_enum.create(op.get_bind(), checkfirst=True)
    opportunity_tier_enum.create(op.get_bind(), checkfirst=True)
    activation_response_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("location_lng", sa.Float(), nullable=True),
        sa.Column("location_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "comfort_level",
            comfort_level_enum,
            nullable=False,
            server_default=sa.text("'solo_ok'"),
        ),
        sa.Column(
            "willingness_radius_km",
            sa.Float(),
            nullable=False,
            server_default=sa.text("5"),
        ),
        sa.Column(
            "activation_stage",
            activation_stage_enum,
            nullable=False,
            server_default=sa.text("'suggest'"),
        ),
        sa.Column(
            "timezone",
            sa.String(length=64),
            nullable=False,
            server_default=sa.text("'UTC'"),
        ),
        sa.Column("push_subscription", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("explicit", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_preferences_user_category",
        "user_preferences",
        ["user_id", "category"],
        unique=False,
    )

    op.create_table(
        "venues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("location", Geography(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("venue_type", sa.String(length=64), nullable=True),
        sa.Column("capacity_estimate", sa.Integer(), nullable=True),
        sa.Column("vibe_tags", postgresql.ARRAY(sa.String(length=64)), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_venues_location",
        "venues",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("venue_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tier", opportunity_tier_enum, nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("cost_pence", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=64)), nullable=True),
        sa.Column("attendee_count_estimate", sa.Integer(), nullable=True),
        sa.Column("solo_friendly_score", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["venue_id"], ["venues.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_starts_at", "events", ["starts_at"], unique=False)
    op.create_index("ix_events_tier", "events", ["tier"], unique=False)
    op.create_index("ix_events_tags", "events", ["tags"], unique=False, postgresql_using="gin")

    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tier", opportunity_tier_enum, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("walk_minutes", sa.Integer(), nullable=True),
        sa.Column("travel_description", sa.Text(), nullable=True),
        sa.Column("social_proof_text", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", Geography(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunities_location",
        "opportunities",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "activations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "shown_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("response", activation_response_enum, nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attended", sa.Boolean(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activations_user_shown_at",
        "activations",
        ["user_id", "shown_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_activations_user_shown_at", table_name="activations")
    op.drop_table("activations")

    op.drop_index("ix_opportunities_location", table_name="opportunities")
    op.drop_table("opportunities")

    op.drop_index("ix_events_tags", table_name="events", postgresql_using="gin")
    op.drop_index("ix_events_tier", table_name="events")
    op.drop_index("ix_events_starts_at", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_venues_location", table_name="venues", postgresql_using="gist")
    op.drop_table("venues")

    op.drop_index("ix_user_preferences_user_category", table_name="user_preferences")
    op.drop_table("user_preferences")

    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS activation_response")
    op.execute("DROP TYPE IF EXISTS opportunity_tier")
    op.execute("DROP TYPE IF EXISTS activation_stage")
    op.execute("DROP TYPE IF EXISTS comfort_level")
