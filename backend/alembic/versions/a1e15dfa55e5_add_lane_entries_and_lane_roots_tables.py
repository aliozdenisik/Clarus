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
    """Upgrade schema."""
    op.create_table(
        "lane_entries",
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
    op.create_index(op.f("ix_lane_entries_broot"), "lane_entries", ["broot"], unique=False)
    op.create_index(op.f("ix_lane_entries_root"), "lane_entries", ["root"], unique=False)
    op.create_table(
        "lane_roots",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("word", sa.String(length=50), nullable=True),
        sa.Column("bword", sa.String(length=50), nullable=True),
        sa.Column("letter", sa.String(length=20), nullable=True),
        sa.Column("bletter", sa.String(length=20), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
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
