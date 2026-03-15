import os
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_VERSIONS_DIR = BACKEND_ROOT / "alembic" / "versions"


def run_alembic_upgrade_head() -> int:
    env = os.environ.copy()
    env["SUPABASE_DB_URL"] = env.get(
        "SUPABASE_DB_URL",
        "postgresql+asyncpg://firstmove:password@localhost:5432/firstmove",
    )
    process = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return process.returncode


def run_alembic_downgrade_base() -> int:
    env = os.environ.copy()
    env["SUPABASE_DB_URL"] = env.get(
        "SUPABASE_DB_URL",
        "postgresql+asyncpg://firstmove:password@localhost:5432/firstmove",
    )
    process = subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "head:base", "--sql"],
        cwd=BACKEND_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    return process.returncode


def test_alembic_upgrade_head_runs():
    assert run_alembic_upgrade_head() == 0


def test_alembic_downgrade_base_runs():
    assert run_alembic_downgrade_base() == 0


def test_initial_migration_exists():
    migration_files = list(ALEMBIC_VERSIONS_DIR.glob("*.py"))
    assert migration_files, "Expected at least one migration script."
