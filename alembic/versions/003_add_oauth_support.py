"""Add OAuth support: nullable password, oauth_provider column

Revision ID: 003
Revises: 002
Create Date: 2026-02-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=True)
    op.add_column("users", sa.Column("oauth_provider", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "oauth_provider")
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False)
