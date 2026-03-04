"""Add subscription tier and Razorpay fields to users

Revision ID: 007
Revises: 006
Create Date: 2026-03-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("subscription_tier", sa.String(20), server_default="free", nullable=False),
    )
    op.add_column("users", sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("razorpay_customer_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("razorpay_subscription_id", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "razorpay_subscription_id")
    op.drop_column("users", "razorpay_customer_id")
    op.drop_column("users", "subscription_expires_at")
    op.drop_column("users", "subscription_tier")
