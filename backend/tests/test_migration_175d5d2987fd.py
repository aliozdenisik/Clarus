from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    import types

MIGRATION_FILE = (
    Path(__file__).resolve().parent.parent
    / "alembic"
    / "versions"
    / "175d5d2987fd_convert_user_id_to_text_for_better_auth.py"
)

DIGITS_ONLY_RE = re.compile(r"^[0-9]+$")

BETTER_AUTH_IDS = [
    "XizxohyfES2viscnjrvfXebFodasHqg6",
    "enQGNTfx63cY9QAaDJmEqxfgeF3QXNCQ",
    "90NzJJyU9RNHhJ7FvVpAEdTiZSg0G1SP",
    "abc123",
    "a1b2c3d4e5f6",
]

LEGACY_NUMERIC_IDS = [
    "1",
    "42",
    "1000",
    "999999",
]


@pytest.fixture
def migration_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("migration_175d5d2987fd", MIGRATION_FILE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_regex_rejects_better_auth_alphanumeric_ids() -> None:
    for ba_id in BETTER_AUTH_IDS:
        assert not DIGITS_ONLY_RE.match(ba_id), f"Should reject '{ba_id}'"


def test_regex_accepts_legacy_numeric_ids() -> None:
    for num_id in LEGACY_NUMERIC_IDS:
        assert DIGITS_ONLY_RE.match(num_id), f"Should accept '{num_id}'"


def test_regex_rejects_uuid_format() -> None:
    assert not DIGITS_ONLY_RE.match("550e8400-e29b-41d4-a716-446655440000")


def test_regex_rejects_empty_string() -> None:
    assert not DIGITS_ONLY_RE.match("")


def test_migration_revision_metadata(migration_module: types.ModuleType) -> None:
    assert migration_module.revision == "175d5d2987fd"
    assert migration_module.down_revision is None


def test_downgrade_deletes_non_numeric_ids_before_cast(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.downgrade()

    execute_calls = [c for c in mock_op.method_calls if c[0] == "execute"]
    alter_calls = [c for c in mock_op.method_calls if c[0] == "alter_column"]

    assert len(execute_calls) == 2
    assert len(alter_calls) == 2

    for exec_call in execute_calls:
        sql = exec_call[1][0]
        assert "!~ '^[0-9]+$'" in sql


def test_downgrade_delete_precedes_alter_for_each_table(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.downgrade()

    for table in ("user_preferences", "search_history"):
        execute_indices = [i for i, c in enumerate(mock_op.method_calls) if c[0] == "execute" and table in str(c[1])]
        alter_indices = [i for i, c in enumerate(mock_op.method_calls) if c[0] == "alter_column" and c[1][0] == table]
        assert execute_indices, f"No DELETE for {table}"
        assert alter_indices, f"No ALTER for {table}"
        assert execute_indices[0] < alter_indices[0], f"DELETE must come before ALTER for {table}"


def test_upgrade_does_not_delete_non_numeric_ids(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    execute_calls = [c for c in mock_op.method_calls if c[0] == "execute"]
    for exec_call in execute_calls:
        sql = exec_call[1][0]
        assert "!~ '^[0-9]+$'" not in sql


def test_downgrade_restores_users_legacy_foreign_keys(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.downgrade()

    fk_calls = [c for c in mock_op.method_calls if c[0] == "create_foreign_key"]
    assert len(fk_calls) == 2
    for fk_call in fk_calls:
        assert fk_call[1][2] == "users_legacy"
