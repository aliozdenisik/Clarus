"""add lane_entries and lane_roots tables

Revision ID: a1e15dfa55e5
Revises: 8e81c284eab3
Create Date: 2026-02-10 23:03:33.238050

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1e15dfa55e5"
down_revision: Union[str, Sequence[str], None] = "8e81c284eab3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    autoincrement=False design (addresses issue #213):
    --------------------------------------------------
    Both ``lane_entries`` and ``lane_roots`` use ``autoincrement=False``
    intentionally.  Their ``id`` values are the *original* primary keys from
    the Lane's Arabic-English Lexicon SQLite database (laneslexicon/LexiconDatabase,
    GPL-3.0).  Preserving the source IDs:
      * keeps the import script idempotent (``TRUNCATE`` + ``INSERT`` with
        explicit IDs — no sequence drift across re-imports);
      * makes cross-referencing the upstream SQLite straightforward for
        debugging and auditing;
      * guarantees uniqueness because the upstream dataset is canonical and
        non-overlapping by construction.
    No sequence / serial column is needed.  See ``backend/scripts/import_lane_lexicon.py``
    for the import logic and ``docs/DATABASE_MIGRATIONS.md`` for the wider
    rationale.

    Index-creation strategy (addresses issue #212):
    -----------------------------------------------
    Indexes below use standard ``op.create_index()`` (without CONCURRENTLY)
    because both tables are *brand-new* and always empty at migration time.
    See ``backend/alembic/versions/8e81c284eab3_add_qm_root_etymologies_table.py``
    and ``docs/DATABASE_MIGRATIONS.md`` for the full CONCURRENTLY policy.
    """
    op.create_table(
        "lane_entries",
        # autoincrement=False: IDs are preserved from Lane's Lexicon source
        # (see docstring above).
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("root", sa.String(length=50), nullable=True),
        sa.Column("broot", sa.String(length=50), nullable=True),
        sa.Column("word", sa.Text(), nullable=True),
        sa.Column("bword", sa.Text(), nullable=True),
        sa.Column("xml", sa.Text(), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("headword", sa.Text(), nullable=True),
        sa.Column("itype", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # Safe without CONCURRENTLY — table is empty at this point (see docstring).
    op.create_index(op.f("ix_lane_entries_broot"), "lane_entries", ["broot"], unique=False)
    op.create_index(op.f("ix_lane_entries_root"), "lane_entries", ["root"], unique=False)
    op.create_table(
        "lane_roots",
        # autoincrement=False: IDs are preserved from Lane's Lexicon source
        # (see docstring above).
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("word", sa.String(length=50), nullable=True),
        sa.Column("bword", sa.String(length=50), nullable=True),
        sa.Column("letter", sa.String(length=20), nullable=True),
        sa.Column("bletter", sa.String(length=20), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # Safe without CONCURRENTLY — table is empty at this point (see docstring).
    op.create_index(op.f("ix_lane_roots_bword"), "lane_roots", ["bword"], unique=False)
    op.create_index(op.f("ix_lane_roots_word"), "lane_roots", ["word"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_lane_roots_word"), table_name="lane_roots")
    op.drop_index(op.f("ix_lane_roots_bword"), table_name="lane_roots")
    op.drop_table("lane_roots")
    op.drop_index(op.f("ix_lane_entries_root"), table_name="lane_entries")
    op.drop_index(op.f("ix_lane_entries_broot"), table_name="lane_entries")
    op.drop_table("lane_entries")
