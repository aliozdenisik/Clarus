from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
import sqlalchemy as sa

if TYPE_CHECKING:
    import types

MIGRATION_FILE = (
    Path(__file__).resolve().parent.parent / "alembic" / "versions" / "d7f8e9a0b1c2_add_onboarding_columns.py"
)


@pytest.fixture
def migration_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("migration_d7f8e9a0b1c2", MIGRATION_FILE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_revision_metadata(migration_module: types.ModuleType) -> None:
    assert migration_module.revision == "d7f8e9a0b1c2"
    assert migration_module.down_revision == "c1a2b3c4d5e6"


def test_upgrade_does_not_use_raw_update_all_rows(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    execute_calls = [c for c in mock_op.method_calls if c[0] == "execute"]
    for exec_call in execute_calls:
        sql_arg = str(exec_call[1][0])
        assert "UPDATE user_preferences SET onboarding_completed" not in sql_arg


def test_upgrade_adds_onboarding_column_with_server_default_true(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    add_column_calls = [c for c in mock_op.method_calls if c[0] == "add_column"]
    onboarding_calls = [
        c
        for c in add_column_calls
        if len(c[1]) >= 2 and hasattr(c[1][1], "name") and c[1][1].name == "onboarding_completed"
    ]
    assert len(onboarding_calls) == 1, "Expected exactly one add_column for onboarding_completed"

    column = onboarding_calls[0][1][1]
    assert str(column.server_default.arg) == "true"


def test_upgrade_switches_server_default_to_false(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    alter_calls = [c for c in mock_op.method_calls if c[0] == "alter_column"]
    onboarding_alters = [c for c in alter_calls if len(c[1]) >= 2 and c[1][1] == "onboarding_completed"]
    assert len(onboarding_alters) == 1, "Expected exactly one alter_column for onboarding_completed"
    assert onboarding_alters[0][2]["server_default"] == "false"


def test_upgrade_alter_column_follows_add_column(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    all_calls = mock_op.method_calls
    add_indices = [
        i
        for i, c in enumerate(all_calls)
        if c[0] == "add_column"
        and len(c[1]) >= 2
        and hasattr(c[1][1], "name")
        and c[1][1].name == "onboarding_completed"
    ]
    alter_indices = [
        i
        for i, c in enumerate(all_calls)
        if c[0] == "alter_column" and len(c[1]) >= 2 and c[1][1] == "onboarding_completed"
    ]
    assert add_indices and alter_indices
    assert add_indices[0] < alter_indices[0], "add_column must precede alter_column"


def test_upgrade_insert_uses_sa_text_with_bindparams(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    execute_calls = [c for c in mock_op.method_calls if c[0] == "execute"]
    insert_calls = [c for c in execute_calls if "INSERT INTO user_preferences" in str(c[1][0])]
    assert len(insert_calls) == 1, "Expected exactly one INSERT execute call"

    sql_obj = insert_calls[0][1][0]
    assert isinstance(sql_obj, sa.TextClause), "INSERT must use sa.text(), not a raw string"


def test_upgrade_insert_uses_bind_parameters_not_literals(
    migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    execute_calls = [c for c in mock_op.method_calls if c[0] == "execute"]
    insert_calls = [c for c in execute_calls if "INSERT INTO user_preferences" in str(c[1][0])]
    sql_text = str(insert_calls[0][1][0])

    for param in (":theme", ":language", ":search_source", ":results_per_page"):
        assert param in sql_text, f"Expected bind parameter {param} in INSERT SQL"

    assert "'system'" not in sql_text, "Literal 'system' should be a bind parameter"
    assert "'tr'" not in sql_text, "Literal 'tr' should be a bind parameter"
    assert "'quran'" not in sql_text, "Literal 'quran' should be a bind parameter"


def test_downgrade_drops_all_four_columns(migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.downgrade()

    drop_calls = [c for c in mock_op.method_calls if c[0] == "drop_column"]
    dropped_columns = {c[1][1] for c in drop_calls}
    expected = {"onboarding_completed", "interests", "arabic_proficiency", "usage_purpose"}
    assert dropped_columns == expected


def test_upgrade_adds_all_four_columns(migration_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_op = MagicMock()
    monkeypatch.setattr(migration_module, "op", mock_op)

    migration_module.upgrade()

    add_calls = [c for c in mock_op.method_calls if c[0] == "add_column"]
    added_columns = {c[1][1].name for c in add_calls if hasattr(c[1][1], "name")}
    expected = {"usage_purpose", "arabic_proficiency", "interests", "onboarding_completed"}
    assert added_columns == expected
