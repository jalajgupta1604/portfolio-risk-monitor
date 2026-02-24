"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON, UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "portfolios",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "holdings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "portfolio_id",
            UUID(as_uuid=True),
            sa.ForeignKey("portfolios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("avg_buy_price", sa.Float, nullable=False),
        sa.Column("current_price", sa.Float, default=0.0),
    )
    op.create_index(
        "ix_holdings_portfolio_symbol",
        "holdings",
        ["portfolio_id", "symbol"],
        unique=True,
    )

    op.create_table(
        "price_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("symbol", sa.String(20), nullable=False, index=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("close", sa.Float, nullable=False),
        sa.Column("volume", sa.Float, default=0.0),
    )
    op.create_index(
        "ix_price_history_symbol_date",
        "price_history",
        ["symbol", "date"],
        unique=True,
    )

    op.create_table(
        "risk_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "portfolio_id",
            UUID(as_uuid=True),
            sa.ForeignKey("portfolios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("rolling_volatility", sa.Float, nullable=False),
        sa.Column("portfolio_beta", sa.Float, nullable=False),
        sa.Column("downside_beta", sa.Float, nullable=False),
        sa.Column("var_95", sa.Float, nullable=False),
        sa.Column("composite_score", sa.Float, nullable=False),
        sa.Column("risk_acceleration", sa.Float, default=0.0),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("correlation_matrix", JSON, default={}),
        sa.Column("stress_results", JSON, default={}),
        sa.Column("weights", JSON, default={}),
    )
    op.create_index(
        "ix_risk_snapshots_portfolio_date",
        "risk_snapshots",
        ["portfolio_id", "computed_at"],
    )


def downgrade() -> None:
    op.drop_table("risk_snapshots")
    op.drop_table("price_history")
    op.drop_table("holdings")
    op.drop_table("portfolios")
