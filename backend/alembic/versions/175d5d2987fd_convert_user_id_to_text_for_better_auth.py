"""convert_user_id_to_text_for_better_auth

Migration: search_history.user_id and user_preferences.user_id from INTEGER
(referencing users_legacy.id) to TEXT (referencing Better Auth user.id).

This migration was originally applied as direct SQL. This file codifies it
so the schema change survives DB recreations.

Revision ID: 175d5d2987fd
Revises:
Create Date: 2026-02-07 08:00:03.355739

Locking behaviour (PostgreSQL):
    ALTER COLUMN TYPE acquires an ACCESS EXCLUSIVE lock on the table, which
    blocks ALL concurrent reads and writes until the rewrite completes.
    For the current deployment this is acceptable because search_history and
    user_preferences are small tables (< 10 000 rows).

    For larger deployments, prefer the expand-contract pattern instead:
      1. Add a new TEXT column (milliseconds, brief lock).
      2. Backfill in batches with UPDATE ... LIMIT.
      3. Rename columns in a single transaction (metadata-only, brief lock).
    See docs/guides/DEPLOYMENT.md for details.
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "175d5d2987fd"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert user_id columns from INTEGER (legacy) to TEXT (Better Auth).

    Lock impact:
        Each ALTER COLUMN TYPE acquires an ACCESS EXCLUSIVE lock on the
        affected table, causing a full table rewrite plus sequential scan.
        During this window every other transaction that touches the table
        will block.  On the current deployment the tables are small enough
        that the lock is held for < 1 s.

        If the tables grow to > 100 000 rows, switch to the expand-contract
        pattern documented in the module docstring.
    """

    # --- search_history ---
    # Drop old FK to users_legacy
    op.drop_constraint("search_history_user_id_fkey", "search_history", type_="foreignkey")
    op.alter_column(
        "search_history",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.String(255),
        existing_nullable=False,
        postgresql_using="user_id::TEXT",
    )
    op.execute('DELETE FROM search_history WHERE user_id NOT IN (SELECT id FROM "user")')
    # Add new FK to Better Auth user table
    op.create_foreign_key(
        "search_history_user_id_fkey",
        "search_history",
        "user",
        ["user_id"],
        ["id"],
    )

    # --- user_preferences ---
    # Drop old FK to users_legacy
    op.drop_constraint("user_preferences_user_id_fkey", "user_preferences", type_="foreignkey")
    op.alter_column(
        "user_preferences",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.String(255),
        existing_nullable=False,
        postgresql_using="user_id::TEXT",
    )
    # Add new FK to Better Auth user table
    op.create_foreign_key(
        "user_preferences_user_id_fkey",
        "user_preferences",
        "user",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Revert user_id columns back to INTEGER (referencing users_legacy).

    Better Auth generates 32-character alphanumeric string IDs by default
    (e.g. ``XizxohyfES2viscnjrvfXebFodasHqg6``).  These **cannot** be cast
    to INTEGER.

    This downgrade therefore:
      1. Deletes rows whose ``user_id`` contains non-numeric characters
         (Better Auth-era data that has no ``users_legacy`` counterpart).
      2. Casts the remaining numeric-only ``user_id`` values to INTEGER.
      3. Restores the foreign key to ``users_legacy``.

    If the database contains *only* Better Auth users (no legacy numeric
    IDs), all rows in the affected tables will be deleted.  Always take a
    backup before running ``alembic downgrade``.
    """

    # --- user_preferences ---
    op.drop_constraint("user_preferences_user_id_fkey", "user_preferences", type_="foreignkey")
    op.execute("DELETE FROM user_preferences WHERE user_id !~ '^[0-9]+$'")
    op.alter_column(
        "user_preferences",
        "user_id",
        existing_type=sa.String(255),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="user_id::INTEGER",
    )
    op.create_foreign_key(
        "user_preferences_user_id_fkey",
        "user_preferences",
        "users_legacy",
        ["user_id"],
        ["id"],
    )

    # --- search_history ---
    op.drop_constraint("search_history_user_id_fkey", "search_history", type_="foreignkey")
    op.execute("DELETE FROM search_history WHERE user_id !~ '^[0-9]+$'")
    op.alter_column(
        "search_history",
        "user_id",
        existing_type=sa.String(255),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="user_id::INTEGER",
    )
    op.create_foreign_key(
        "search_history_user_id_fkey",
        "search_history",
        "users_legacy",
        ["user_id"],
        ["id"],
    )
