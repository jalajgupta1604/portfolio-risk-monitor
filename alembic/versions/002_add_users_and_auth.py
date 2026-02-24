"""Add users table and user_id to portfolios

Revision ID: 002
Revises: 001
Create Date: 2026-02-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Default admin user ID (deterministic so backfill is reproducible)
DEFAULT_USER_ID = "00000000-0000-4000-a000-000000000001"


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 2. Insert a default admin user (password: "admin123" hashed with bcrypt)
    op.execute(
        sa.text(
            "INSERT INTO users (id, email, hashed_password, full_name) "
            "VALUES (:id, :email, :pw, :name)"
        ).bindparams(
            id=DEFAULT_USER_ID,
            email="admin@riskmonitor.local",
            # bcrypt hash of "admin123"
            pw="$2b$12$Zxb6FkJD6HIrSvzQX2cTq.qLHaHW5BQbR2h0nokRf0qfxG9mOt8Va",
            name="Default Admin",
        )
    )

    # 3. Add user_id column (nullable first so we can backfill)
    op.add_column(
        "portfolios",
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
    )

    # 4. Backfill existing portfolios to default admin user
    op.execute(
        sa.text("UPDATE portfolios SET user_id = :uid WHERE user_id IS NULL").bindparams(
            uid=DEFAULT_USER_ID
        )
    )

    # 5. Set NOT NULL constraint and add FK
    op.alter_column("portfolios", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_portfolios_user_id",
        "portfolios",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_portfolios_user_id", "portfolios", type_="foreignkey")
    op.drop_column("portfolios", "user_id")
    op.drop_table("users")
