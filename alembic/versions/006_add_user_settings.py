"""Add phone_number and whatsapp_alerts_enabled to users

Revision ID: 006
Revises: 005
Create Date: 2026-03-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(20), nullable=True))
    op.add_column(
        "users",
        sa.Column("whatsapp_alerts_enabled", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "whatsapp_alerts_enabled")
    op.drop_column("users", "phone_number")
