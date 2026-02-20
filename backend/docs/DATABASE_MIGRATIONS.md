# Database Migration Guidelines

This document records project-wide conventions for Alembic migrations so that
future contributors apply consistent, safe DDL patterns.

---

## Index Creation Strategy (Issue #212)

### Rule: use CONCURRENTLY only for populated tables

PostgreSQL acquires an `AccessExclusiveLock` during `CREATE INDEX`, blocking
all reads **and** writes until the build completes.  For large tables this can
cause application timeouts.  `CREATE INDEX CONCURRENTLY` avoids this by
building the index in the background, but it comes with two constraints:

1. It **cannot run inside a transaction**.
2. It takes roughly twice as long as a standard index build.

Alembic wraps every migration in a transaction by default, so the two
approaches have different requirements.

### Decision matrix

| Table state at migration time | Recommended approach |
|-------------------------------|----------------------|
| **New / empty** (created in the same migration) | `op.create_index()` — lock is released in microseconds, CONCURRENTLY provides no benefit |
| **Populated** (index added to an existing table) | `op.execute("CREATE INDEX CONCURRENTLY ...")` in a dedicated, non-transactional migration |

### How to write a non-transactional migration for a populated table

```python
# backend/alembic/versions/<rev>_add_idx_on_large_table.py

from alembic import op
from sqlalchemy import text


def upgrade() -> None:
    # Must run outside the implicit Alembic transaction.
    connection = op.get_bind()
    connection.execute(text("COMMIT"))  # end Alembic's transaction
    connection.execute(
        text("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_my_table_col ON my_table (col)")
    )
    # Do NOT open a new transaction here — Alembic will do it on the next step.


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(text("COMMIT"))
    connection.execute(text("DROP INDEX CONCURRENTLY IF EXISTS idx_my_table_col"))
```

> **Warning**: This pattern exits Alembic's transaction, so DDL in the same
> `upgrade()` function that runs *after* the `COMMIT` is no longer atomic.
> Limit non-transactional migrations to a single `CREATE INDEX CONCURRENTLY`
> statement per file.

### Existing migrations

The migrations below create indexes on brand-new empty tables and therefore
use `op.create_index()` without `CONCURRENTLY` — this is intentional and safe:

| Migration | Tables | Rationale |
|-----------|--------|-----------|
| `8e81c284eab3` | `qm_root_etymologies` | Table is new and empty at migration time |
| `a1e15dfa55e5` | `lane_entries`, `lane_roots` | Tables are new and empty at migration time |

---

## Manual ID Assignment (Issue #213)

### Rule: autoincrement=False is acceptable for external-source tables

Some tables store data imported from an external, canonical dataset where the
source system already assigns stable, non-overlapping primary keys.  For these
tables, setting `autoincrement=False` on the `id` column and preserving the
source IDs is preferred because:

* The import script becomes **idempotent**: `TRUNCATE` + `INSERT` with explicit
  IDs is safe to re-run without sequence drift.
* Cross-referencing the upstream dataset for debugging is straightforward.
* Uniqueness is guaranteed by the canonical nature of the source data.

### Affected tables

| Table | Source | ID origin |
|-------|--------|-----------|
| `lane_entries` | Lane's Arabic-English Lexicon (laneslexicon/LexiconDatabase, GPL-3.0) | SQLite `entry.id` |
| `lane_roots` | Lane's Arabic-English Lexicon | SQLite `root.id` |

The import script `backend/scripts/import_lane_lexicon.py` performs
`TRUNCATE TABLE lane_entries, lane_roots` before every import run, making
re-imports safe.

### When to use autoincrement=True instead

Use `autoincrement=True` (the default) whenever:

* IDs have no meaning outside the database.
* The table is populated by application logic (not a one-time data import).
* Multiple import sources could produce overlapping IDs.
