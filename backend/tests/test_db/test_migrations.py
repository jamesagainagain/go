import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_VERSIONS_DIR = BACKEND_ROOT / "alembic" / "versions"


def _resolve_test_db_url() -> str | None:
    return (
        os.environ.get("TEST_MIGRATION_DB_URL")
        or os.environ.get("SUPABASE_DB_URL")
        or os.environ.get("DATABASE_URL")
    )


def run_alembic_command(*command: str, render_sql: bool, db_url: str | None = None) -> int:
    env = os.environ.copy()
    if db_url:
        env["SUPABASE_DB_URL"] = db_url
    else:
        env["SUPABASE_DB_URL"] = env.get(
            "SUPABASE_DB_URL",
            "postgresql+asyncpg://firstmove:password@localhost:5432/firstmove",
        )

    alembic_command = [sys.executable, "-m", "alembic", *command]
    if render_sql:
        alembic_command.append("--sql")

    process = subprocess.run(
        alembic_command,
        cwd=BACKEND_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return process.returncode


def test_alembic_upgrade_head_runs():
    assert run_alembic_command("upgrade", "head", render_sql=True) == 0


def test_alembic_downgrade_base_runs():
    assert run_alembic_command("downgrade", "head:base", render_sql=True) == 0


def test_initial_migration_exists():
    migration_files = list(ALEMBIC_VERSIONS_DIR.glob("*.py"))
    assert migration_files, "Expected at least one migration script."


@pytest.mark.integration
def test_live_upgrade_and_downgrade_when_db_available():
    db_url = _resolve_test_db_url()
    if not db_url:
        pytest.skip("No TEST_MIGRATION_DB_URL/SUPABASE_DB_URL/DATABASE_URL configured.")

    # Skip if DB is unreachable (Docker not running, wrong credentials, etc.)
    try:
        import asyncio
        import asyncpg
        from sqlalchemy.engine import make_url
        url = make_url(db_url)
        # asyncpg uses postgresql:// not postgresql+asyncpg://
        pg_url = url.set(drivername="postgresql").render_as_string(hide_password=False)
        asyncio.run(asyncpg.connect(pg_url)).close()
    except Exception:
        pytest.skip("Database unreachable (run 'make up' for Docker Postgres).")

    assert run_alembic_command("upgrade", "head", render_sql=False, db_url=db_url) == 0
    assert run_alembic_command("downgrade", "base", render_sql=False, db_url=db_url) == 0
