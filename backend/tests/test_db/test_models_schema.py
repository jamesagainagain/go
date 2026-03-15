from sqlalchemy import ForeignKeyConstraint

import app.models  # noqa: F401
from app.database import Base

EXPECTED_TABLES = {
    "users",
    "user_preferences",
    "venues",
    "events",
    "opportunities",
    "activations",
}


def test_expected_tables_registered():
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))


def test_uuid_primary_keys_have_server_defaults():
    for table_name in EXPECTED_TABLES:
        table = Base.metadata.tables[table_name]
        id_column = table.c.id
        assert id_column.server_default is not None


def test_critical_foreign_keys_exist():
    fk_map = {
        "user_preferences": {("user_id", "users.id")},
        "events": {("venue_id", "venues.id")},
        "opportunities": {("event_id", "events.id")},
        "activations": {("user_id", "users.id"), ("opportunity_id", "opportunities.id")},
    }

    for table_name, expected_links in fk_map.items():
        table = Base.metadata.tables[table_name]
        constraints = {
            (fk.parent.name, f"{fk.column.table.name}.{fk.column.name}")
            for constraint in table.constraints
            if isinstance(constraint, ForeignKeyConstraint)
            for fk in constraint.elements
        }
        assert expected_links.issubset(constraints)
