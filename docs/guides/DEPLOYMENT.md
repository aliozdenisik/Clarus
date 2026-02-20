# Deployment Guide

## Database Migrations

Clarus uses [Alembic](https://alembic.sqlalchemy.org/) for schema management.
All migrations live in `backend/alembic/versions/`.

### Running Migrations

```bash
cd backend
uv run alembic upgrade head      # apply all pending migrations
uv run alembic downgrade -1      # roll back one migration
uv run alembic history           # list migration chain
```

### Migration: `175d5d2987fd` — Convert user_id to TEXT (Better Auth)

| Property | Value |
|----------|-------|
| Tables affected | `search_history`, `user_preferences` |
| Column | `user_id` |
| Change | `INTEGER` → `TEXT (VARCHAR 255)` |
| Lock type | `ACCESS EXCLUSIVE` (blocks all reads and writes) |
| Reversible | Partial — see **Downgrade Caveats** below |

#### Why This Migration Exists

The project migrated from a custom integer-keyed `users_legacy` table to
[Better Auth](https://www.better-auth.com/), which generates 32-character
alphanumeric string IDs (e.g. `XizxohyfES2viscnjrvfXebFodasHqg6`).  The
`user_id` foreign key columns in `search_history` and `user_preferences`
must be `TEXT` to reference the Better Auth `user` table.

#### Lock Impact

`ALTER COLUMN TYPE` acquires an **ACCESS EXCLUSIVE** lock on each table.
This is the most restrictive PostgreSQL lock — it blocks every other
transaction (reads included) until the table rewrite completes.

| Table size | Expected lock duration | Recommended approach |
|------------|------------------------|----------------------|
| < 10 000 rows | < 1 second | Direct `ALTER` (current migration) |
| 10 000 – 100 000 rows | 1 – 10 seconds | Schedule maintenance window |
| > 100 000 rows | 10+ seconds | Use expand-contract pattern |

**Expand-contract pattern** (zero-downtime alternative):

1. `ALTER TABLE ADD COLUMN user_id_new TEXT` — milliseconds, brief lock.
2. Create a trigger to sync writes from `user_id` → `user_id_new`.
3. Backfill in batches: `UPDATE ... WHERE user_id_new IS NULL LIMIT 5000`.
4. `ALTER TABLE RENAME COLUMN` swap in a single transaction — metadata-only.
5. Drop the old column in a follow-up migration after verification.

#### Downgrade Caveats

Better Auth IDs are **non-numeric strings**.  The downgrade function handles
this by deleting rows whose `user_id` does not match `'^[0-9]+$'` before
casting back to `INTEGER`.

**Consequences:**

- Any search history or preferences created under Better Auth will be
  **permanently deleted** during downgrade.
- If the database contains *only* Better Auth users (no legacy numeric IDs),
  both tables will be emptied.
- **Always take a full backup** before running `alembic downgrade`.

```bash
# Recommended downgrade procedure
pg_dump -Fc -d postgres -h localhost -p 54322 -U postgres > backup_before_downgrade.dump
cd backend
uv run alembic downgrade 175d5d2987fd-1
```
