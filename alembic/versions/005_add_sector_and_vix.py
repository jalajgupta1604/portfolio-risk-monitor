"""Add sector column to holdings and sector_concentration to risk_snapshots

Revision ID: 005
Revises: 004
Create Date: 2026-03-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("holdings", sa.Column("sector", sa.String(100), nullable=True))
    op.add_column(
        "risk_snapshots",
        sa.Column("sector_concentration", sa.Float(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("risk_snapshots", "sector_concentration")
    op.drop_column("holdings", "sector")
