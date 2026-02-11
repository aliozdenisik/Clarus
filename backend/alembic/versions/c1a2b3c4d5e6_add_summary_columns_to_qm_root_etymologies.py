"""add summary_tr and summary_en to qm_root_etymologies

Revision ID: c1a2b3c4d5e6
Revises: a1e15dfa55e5
Create Date: 2026-02-11 20:30:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "a1e15dfa55e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("qm_root_etymologies", sa.Column("summary_tr", sa.Text(), nullable=True))
    op.add_column("qm_root_etymologies", sa.Column("summary_en", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("qm_root_etymologies", "summary_en")
    op.drop_column("qm_root_etymologies", "summary_tr")
