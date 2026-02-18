"""add_onboarding_columns

Add onboarding-related columns to user_preferences:
- usage_purpose: enum field (academic, personal, preaching, comparative, textual)
- arabic_proficiency: enum field (none, basic, intermediate, advanced)
- interests: JSON array of strings
- onboarding_completed: boolean flag (default false for new users, true for existing)

This migration sets onboarding_completed=true for all existing rows to prevent
existing users from being forced through onboarding flow.

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

    # Add the 4 new columns
    op.add_column("user_preferences", sa.Column("usage_purpose", sa.String(30), nullable=True))
    op.add_column("user_preferences", sa.Column("arabic_proficiency", sa.String(20), nullable=True))
    op.add_column("user_preferences", sa.Column("interests", sa.JSON(), nullable=True))
    op.add_column(
        "user_preferences", sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="false")
    )

    # Mark all existing user_preferences rows as onboarding_completed=true
    # This prevents existing users from being redirected to onboarding flow
    op.execute("UPDATE user_preferences SET onboarding_completed = true")

    # Ensure all Better Auth users have a corresponding user_preferences row
    # with onboarding_completed=true (for users who haven't set preferences yet)
    op.execute(
        """
        INSERT INTO user_preferences (user_id, theme, language, default_search_source,
                                      results_per_page, enable_streaming, enable_multi_agent,
                                      onboarding_completed, updated_at)
        SELECT u.id, 'system', 'tr', 'quran', 10, true, true, true, NOW()
        FROM "user" u
        WHERE u.id NOT IN (SELECT user_id FROM user_preferences)
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade: Remove the 4 onboarding columns from user_preferences."""
    op.drop_column("user_preferences", "onboarding_completed")
    op.drop_column("user_preferences", "interests")
    op.drop_column("user_preferences", "arabic_proficiency")
    op.drop_column("user_preferences", "usage_purpose")
