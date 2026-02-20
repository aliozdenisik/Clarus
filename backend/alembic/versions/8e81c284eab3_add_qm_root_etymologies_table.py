"""add_qm_root_etymologies_table

Revision ID: 8e81c284eab3
Revises: 175d5d2987fd
Create Date: 2026-02-10 21:46:24.800614

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e81c284eab3"
down_revision: Union[str, Sequence[str], None] = "175d5d2987fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Index-creation strategy (addresses issue #212):
    -----------------------------------------------
    Indexes below use standard ``op.create_index()`` (without CONCURRENTLY)
    because ``qm_root_etymologies`` is a *brand-new* table created in this
    same migration.  At migration time the table is always empty, so the
    ``AccessExclusiveLock`` acquired during index build is released in
    microseconds — functionally identical to a concurrent build.

    ``CREATE INDEX CONCURRENTLY`` is reserved for adding indexes to tables
    that already hold significant data (i.e., separate, post-populate
    migrations).  Using it here would require running outside a transaction
    (PostgreSQL restriction) with no benefit to offer.

    See ``docs/DATABASE_MIGRATIONS.md`` for the project-wide concurrency
    strategy.
    """
    op.create_table(
        "qm_root_etymologies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("root", sa.String(length=20), nullable=False),
        sa.Column("root_buckwalter", sa.String(length=20), nullable=False),
        sa.Column("definition_en", sa.Text(), nullable=True),
        sa.Column("definition_tr", sa.Text(), nullable=True),
        sa.Column("semantic_field", sa.String(length=100), nullable=True),
        sa.Column("morphological_forms", sa.JSON(), nullable=True),
        sa.Column("related_roots", sa.JSON(), nullable=True),
        sa.Column("quran_frequency", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("lane_match_type", sa.String(length=20), nullable=True),
        sa.Column("lane_volume", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.String(length=20), nullable=False, server_default=sa.text("'low'")),
        sa.Column("tr_translation_source", sa.String(length=50), nullable=True),
        sa.Column("tr_translation_confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    # Safe without CONCURRENTLY — table is empty at this point (see docstring).
    op.create_index(op.f("ix_qm_root_etymologies_root"), "qm_root_etymologies", ["root"], unique=True)
    op.create_index(
        op.f("ix_qm_root_etymologies_root_buckwalter"),
        "qm_root_etymologies",
        ["root_buckwalter"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_qm_root_etymologies_root_buckwalter"), table_name="qm_root_etymologies")
    op.drop_index(op.f("ix_qm_root_etymologies_root"), table_name="qm_root_etymologies")
    op.drop_table("qm_root_etymologies")
