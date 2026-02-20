"""add_onboarding_columns

Add onboarding-related columns to user_preferences:
- usage_purpose: enum field (academic, personal, preaching, comparative, textual)
- arabic_proficiency: enum field (none, basic, intermediate, advanced)
- interests: JSON array of strings
- onboarding_completed: boolean flag (default false for new users, true for existing)

Existing users receive onboarding_completed=true via a two-step server_default
approach that avoids a full-table UPDATE scan:

1. ADD COLUMN with server_default='true'  — PG 11+ metadata-only operation,
   existing rows materialise the default lazily on read (zero row locks).
2. ALTER COLUMN SET DEFAULT 'false'       — future INSERTs get false so new
   users are routed through the onboarding flow.

Revision ID: d7f8e9a0b1c2
Revises: c1a2b3c4d5e6
Create Date: 2026-02-18 12:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7f8e9a0b1c2"
down_revision: Union[str, Sequence[str], None] = "c1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade: Add 4 onboarding columns to user_preferences."""

    op.add_column("user_preferences", sa.Column("usage_purpose", sa.String(30), nullable=True))
    op.add_column("user_preferences", sa.Column("arabic_proficiency", sa.String(20), nullable=True))
    op.add_column("user_preferences", sa.Column("interests", sa.JSON(), nullable=True))

    # server_default='true' so existing rows get true via PG 11+ metadata-only fast path
    op.add_column(
        "user_preferences",
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="true"),
    )

    # Switch default to 'false' for future inserts (new users enter onboarding)
    op.alter_column(
        "user_preferences",
        "onboarding_completed",
        server_default="false",
        existing_type=sa.Boolean(),
        existing_nullable=False,
    )

    # Backfill preferences for Better Auth users that don't have a row yet
    op.execute(
        sa.text(
            """
            INSERT INTO user_preferences (user_id, theme, language, default_search_source,
                                          results_per_page, enable_streaming, enable_multi_agent,
                                          onboarding_completed, updated_at)
            SELECT u.id, :theme, :language, :search_source,
                   :results_per_page, :streaming, :multi_agent, :onboarded, NOW()
            FROM "user" u
            WHERE u.id NOT IN (SELECT user_id FROM user_preferences)
            ON CONFLICT DO NOTHING
            """
        ).bindparams(
            theme="system",
            language="tr",
            search_source="quran",
            results_per_page=10,
            streaming=True,
            multi_agent=True,
            onboarded=True,
        )
    )


def downgrade() -> None:
    """Downgrade: Remove the 4 onboarding columns from user_preferences."""
    op.drop_column("user_preferences", "onboarding_completed")
    op.drop_column("user_preferences", "interests")
    op.drop_column("user_preferences", "arabic_proficiency")
    op.drop_column("user_preferences", "usage_purpose")
