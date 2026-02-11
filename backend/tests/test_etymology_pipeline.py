"""Tests for Quranic Arabic etymology table schema and ETL pipeline."""

import json
from collections.abc import AsyncGenerator
from importlib import import_module
from pathlib import Path
from typing import Any

import asyncpg
import pytest

etymology_pipeline: Any

try:
    etymology_pipeline = import_module("src.etymology_pipeline")
    FORM_PATTERNS = etymology_pipeline.FORM_PATTERNS
    extract_all_roots_with_frequency = etymology_pipeline.extract_all_roots_with_frequency
    extract_morphological_forms = etymology_pipeline.extract_morphological_forms
    ETYMOLOGY_PIPELINE_AVAILABLE = True
except ModuleNotFoundError:
    etymology_pipeline = None
    FORM_PATTERNS = {}

    def extract_all_roots_with_frequency() -> list[Any]:
        return []

    def extract_morphological_forms(_root: str, _rows: list[tuple[str, str, str, str]]) -> list[dict]:
        return []

    ETYMOLOGY_PIPELINE_AVAILABLE = False

DATABASE_DSN = "postgresql://postgres:postgres@localhost:54322/postgres"
DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"


@pytest.mark.skipif(not ETYMOLOGY_PIPELINE_AVAILABLE, reason="Task 3 etymology pipeline module not yet available")
class TestTranslationThrottleUtilities:
    def test_parse_retry_after_seconds(self) -> None:
        assert etymology_pipeline is not None
        assert etymology_pipeline._parse_retry_after_seconds("5") == 5.0
        assert etymology_pipeline._parse_retry_after_seconds("0.5") == 0.5
        assert etymology_pipeline._parse_retry_after_seconds(None) is None
        assert etymology_pipeline._parse_retry_after_seconds("invalid") is None
        assert etymology_pipeline._parse_retry_after_seconds("0") is None

    def test_parse_positive_int_env_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert etymology_pipeline is not None
        monkeypatch.setenv("ETYMOLOGY_TRANSLATION_WORKERS", "invalid")
        assert etymology_pipeline._parse_positive_int_env("ETYMOLOGY_TRANSLATION_WORKERS", 20) == 20

        monkeypatch.setenv("ETYMOLOGY_TRANSLATION_WORKERS", "0")
        assert etymology_pipeline._parse_positive_int_env("ETYMOLOGY_TRANSLATION_WORKERS", 20) == 20

        monkeypatch.setenv("ETYMOLOGY_TRANSLATION_WORKERS", "12")
        assert etymology_pipeline._parse_positive_int_env("ETYMOLOGY_TRANSLATION_WORKERS", 20) == 12

    def test_translation_throttle_caps_backoff(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert etymology_pipeline is not None

        now = [100.0]
        sleeps: list[float] = []

        monkeypatch.setattr(etymology_pipeline.time, "monotonic", lambda: now[0])
        monkeypatch.setattr(etymology_pipeline.time, "sleep", lambda seconds: sleeps.append(seconds))

        throttle = etymology_pipeline.TranslationThrottle(max_backoff_seconds=30.0)
        throttle.apply_backoff(120.0, reason="unit-test")
        throttle.wait_if_needed()

        assert sleeps == [30.0]


@pytest.fixture(scope="module")
async def conn() -> AsyncGenerator[asyncpg.Connection, None]:
    """Provide an asyncpg connection for schema inspection."""
    connection = await asyncpg.connect(DATABASE_DSN)
    try:
        yield connection
    finally:
        await connection.close()


@pytest.mark.anyio
async def test_qm_root_etymologies_table_exists(conn: asyncpg.Connection) -> None:
    """qm_root_etymologies table should exist after migration."""
    exists = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'qm_root_etymologies'
        )
        """
    )
    assert exists is True


@pytest.mark.anyio
async def test_qm_root_etymologies_has_all_required_columns_and_types(conn: asyncpg.Connection) -> None:
    """qm_root_etymologies should expose all required columns with expected SQL types."""
    rows = await conn.fetch(
        """
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'qm_root_etymologies'
        """
    )
    columns = {
        row["column_name"]: {
            "data_type": row["data_type"],
            "udt_name": row["udt_name"],
        }
        for row in rows
    }

    required_columns = {
        "id": {"data_type": {"integer"}, "udt_name": {"int4"}},
        "root": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "root_buckwalter": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "definition_en": {"data_type": {"text"}, "udt_name": {"text"}},
        "definition_tr": {"data_type": {"text"}, "udt_name": {"text"}},
        "semantic_field": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "morphological_forms": {"data_type": {"json"}, "udt_name": {"json"}},
        "related_roots": {"data_type": {"json"}, "udt_name": {"json"}},
        "quran_frequency": {"data_type": {"integer"}, "udt_name": {"int4"}},
        "source": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "lane_match_type": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "lane_volume": {"data_type": {"integer"}, "udt_name": {"int4"}},
        "confidence": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "tr_translation_source": {"data_type": {"character varying"}, "udt_name": {"varchar"}},
        "tr_translation_confidence": {"data_type": {"double precision"}, "udt_name": {"float8"}},
        "created_at": {"data_type": {"timestamp without time zone"}, "udt_name": {"timestamp"}},
        "updated_at": {"data_type": {"timestamp without time zone"}, "udt_name": {"timestamp"}},
    }

    assert set(required_columns).issubset(columns)

    for column_name, expected_type in required_columns.items():
        assert columns[column_name]["data_type"] in expected_type["data_type"]
        assert columns[column_name]["udt_name"] in expected_type["udt_name"]


async def _has_unique_constraint(conn: asyncpg.Connection, column_name: str) -> bool:
    """Return whether a single-column unique index exists for column_name."""
    count = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM pg_index i
        JOIN pg_class t ON t.oid = i.indrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN unnest(i.indkey::smallint[]) WITH ORDINALITY AS cols(attnum, ord) ON TRUE
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = cols.attnum
        WHERE n.nspname = 'public'
          AND t.relname = 'qm_root_etymologies'
          AND i.indisunique
          AND i.indnatts = 1
          AND cols.ord = 1
          AND a.attname = $1
        """,
        column_name,
    )
    return bool(count and count > 0)


@pytest.mark.anyio
async def test_qm_root_etymologies_root_is_unique(conn: asyncpg.Connection) -> None:
    """root column should have a unique constraint."""
    assert await _has_unique_constraint(conn, "root") is True


@pytest.mark.anyio
async def test_qm_root_etymologies_root_buckwalter_is_unique(conn: asyncpg.Connection) -> None:
    """root_buckwalter column should have a unique constraint."""
    assert await _has_unique_constraint(conn, "root_buckwalter") is True


@pytest.mark.skipif(not ETYMOLOGY_PIPELINE_AVAILABLE, reason="Task 3 etymology pipeline module not yet available")
class TestMorphologicalForms:
    """Morphological form extraction tests (Issue #128 Task 3)."""

    def test_form_patterns_count(self) -> None:
        """FORM_PATTERNS must define at least 20 Arabic form patterns."""
        assert len(FORM_PATTERNS) >= 20

    def test_form_patterns_structure(self) -> None:
        """Each form pattern entry must expose required metadata keys."""
        for pattern in FORM_PATTERNS.values():
            assert "arabic" in pattern
            assert "name" in pattern
            assert "type" in pattern

    def test_extract_forms_known_root(self) -> None:
        """Known root should yield at least one extracted morphological form."""
        rows = [
            (
                "يَكْتُبُونَ",
                "يكتبون",
                "V",
                "IMPF|VF:1|ROOT:كتب|LEM:كَتَبَ|3MP|MOOD:IND || PRON|SUFF|3MP",
            ),
            (
                "مُصَفًّى",
                "مصفى",
                "N",
                "PASS_PCPL|VF:2|ROOT:كتب|LEM:مَكْتُوب|M|INDEF|GEN",
            ),
        ]

        forms = extract_morphological_forms("كتب", rows)
        assert forms
        assert len(forms) >= 1

    def test_extract_forms_returns_counts(self) -> None:
        """Each extracted form entry should include an occurrences count."""
        rows = [
            (
                "كَتَبَتْ",
                "كتبت",
                "V",
                "PERF|VF:1|ROOT:كتب|LEM:كَتَبَ|3FS",
            ),
            (
                "كَتَبُوا",
                "كتبوا",
                "V",
                "PERF|VF:1|ROOT:كتب|LEM:كَتَبَ|3MP",
            ),
        ]

        forms = extract_morphological_forms("كتب", rows)
        assert forms
        assert all("occurrences" in entry for entry in forms)
        assert all(isinstance(entry["occurrences"], int) for entry in forms)

    def test_extract_all_roots(self) -> None:
        """Root extraction should return root entries with frequency counts."""
        roots = extract_all_roots_with_frequency()
        assert roots
        assert len(roots) > 0
        assert all(root.root for root in roots)
        assert all(root.frequency > 0 for root in roots)


class TestLaneAdapter:
    """Lane's Lexicon adapter tests against PostgreSQL (Issue #128 Task 2)."""

    def test_lane_adapter_opens_database(self) -> None:
        from src.lane_lexicon import LaneLexiconAdapter

        adapter = LaneLexiconAdapter(db_url=DATABASE_URL)
        assert adapter._engine is not None

    def test_lane_lookup_known_root(self) -> None:
        from src.lane_lexicon import LaneLexiconAdapter

        adapter = LaneLexiconAdapter(db_url=DATABASE_URL)
        entry = adapter.lookup_by_root("ktb")

        assert entry is not None
        assert entry.root_buckwalter == "ktb"
        assert entry.definition_en is not None
        assert len(entry.definition_en.strip()) > 10

    def test_lane_lookup_nonexistent_root(self) -> None:
        from src.lane_lexicon import LaneLexiconAdapter

        adapter = LaneLexiconAdapter(db_url=DATABASE_URL)
        assert adapter.lookup_by_root("zzzzz") is None

    def test_lane_volume_extraction(self) -> None:
        from src.lane_lexicon import LaneLexiconAdapter

        adapter = LaneLexiconAdapter(db_url=DATABASE_URL)
        entry = adapter.lookup_by_root("ktb")

        assert entry is not None
        assert entry.volume is not None
        assert 1 <= entry.volume <= 8
        assert adapter.get_volume(entry) == entry.volume

    def test_lane_adapter_missing_db(self, tmp_path: Path) -> None:
        from src.lane_lexicon import LaneLexiconAdapter

        missing_dir = tmp_path / "lane_missing"
        with pytest.raises(FileNotFoundError, match=r"Lane.*database"):
            LaneLexiconAdapter(db_path=missing_dir)


@pytest.mark.skipif(not ETYMOLOGY_PIPELINE_AVAILABLE, reason="Task 3 etymology pipeline module not yet available")
class TestEtymologyPipeline:
    """Pipeline integration tests for Issue #128 Task 4."""

    def test_pipeline_runs_corpus_only(self, tmp_path: Path) -> None:
        pipeline_cls = etymology_pipeline.EtymologyPipeline
        pipeline = pipeline_cls(
            db_url=DATABASE_URL,
            lane_db_path=None,
            openrouter_api_key=None,
            dry_run=True,
            use_lane=False,
        )
        result = pipeline.run()

        assert result.success is True
        assert result.total_roots > 0
        assert result.lane_matches == 0

    def test_pipeline_idempotent(self, tmp_path: Path) -> None:
        pipeline_cls = etymology_pipeline.EtymologyPipeline
        pipeline = pipeline_cls(
            db_url=DATABASE_URL,
            lane_db_path=None,
            openrouter_api_key=None,
            dry_run=False,
            use_lane=False,
        )

        first = pipeline.run()
        second = pipeline.run()

        assert first.success is True
        assert second.success is True
        assert first.inserted_rows == second.inserted_rows
        assert first.total_roots == second.total_roots

    def test_pipeline_exports_validation_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        pipeline_cls = etymology_pipeline.EtymologyPipeline
        export_dir = tmp_path / "etymology"
        monkeypatch.setattr(etymology_pipeline, "ETYMOLOGY_EXPORT_DIR", export_dir)

        pipeline = pipeline_cls(
            db_url=DATABASE_URL,
            lane_db_path=None,
            openrouter_api_key=None,
            dry_run=True,
        )
        result = pipeline.run()

        assert result.success is True
        expected_files = {
            "lane_unmatched_roots.json",
            "tr_low_confidence_translations.json",
            "spot_check_sample.json",
        }
        existing_files = {path.name for path in export_dir.glob("*.json")}
        assert expected_files.issubset(existing_files)

        with (export_dir / "spot_check_sample.json").open(encoding="utf-8") as file_handle:
            sample = json.load(file_handle)
        assert isinstance(sample, list)

    def test_pipeline_populates_all_roots(self) -> None:
        pipeline_cls = etymology_pipeline.EtymologyPipeline
        pipeline = pipeline_cls(
            db_url=DATABASE_URL,
            lane_db_path=None,
            openrouter_api_key=None,
            dry_run=False,
        )
        result = pipeline.run()

        assert result.success is True
        assert result.inserted_rows == result.total_roots
        assert result.total_roots >= 1500

    def test_pipeline_handles_lane_missing(self, tmp_path: Path) -> None:
        """When SQLite path is missing, pipeline falls back to PostgreSQL lane_entries."""
        pipeline_cls = etymology_pipeline.EtymologyPipeline
        missing_lane_dir = tmp_path / "does-not-exist"
        pipeline = pipeline_cls(
            db_url=DATABASE_URL,
            lane_db_path=missing_lane_dir,
            openrouter_api_key=None,
            dry_run=True,
        )
        result = pipeline.run()

        assert result.success is True
        # Lane data is in PostgreSQL, so matches are found even without SQLite
        assert result.lane_matches > 0
