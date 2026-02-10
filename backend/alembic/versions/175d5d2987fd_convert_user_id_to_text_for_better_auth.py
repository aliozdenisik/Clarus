"""convert_user_id_to_text_for_better_auth

Migration: search_history.user_id and user_preferences.user_id from INTEGER
(referencing users_legacy.id) to TEXT (referencing Better Auth user.id).

This migration was originally applied as direct SQL. This file codifies it
so the schema change survives DB recreations.

Revision ID: 175d5d2987fd
Revises:
Create Date: 2026-02-07 08:00:03.355739

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
    """Convert user_id columns from INTEGER (legacy) to TEXT (Better Auth)."""

    # --- search_history ---
    # Drop old FK to users_legacy
    op.drop_constraint("search_history_user_id_fkey", "search_history", type_="foreignkey")
    # Change column type from INTEGER to TEXT
    op.alter_column(
        "search_history",
        "user_id",
        existing_type=sa.Integer(),
        type_=sa.String(255),
        existing_nullable=False,
        postgresql_using="user_id::TEXT",
    )
    # Delete orphaned rows that don't have a matching Better Auth user
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
    # Change column type from INTEGER to TEXT
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

    WARNING: This will fail if any user_id values cannot be cast to INTEGER.
    Data loss may occur if Better Auth user IDs are non-numeric strings.
    """

    # --- user_preferences ---
    op.drop_constraint("user_preferences_user_id_fkey", "user_preferences", type_="foreignkey")
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
