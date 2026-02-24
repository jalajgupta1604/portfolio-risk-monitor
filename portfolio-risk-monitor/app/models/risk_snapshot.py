import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"
    __table_args__ = (
        Index("ix_risk_snapshots_portfolio_date", "portfolio_id", "computed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    rolling_volatility: Mapped[float] = mapped_column(Float, nullable=False)
    portfolio_beta: Mapped[float] = mapped_column(Float, nullable=False)
    downside_beta: Mapped[float] = mapped_column(Float, nullable=False)
    var_95: Mapped[float] = mapped_column(Float, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_acceleration: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)

    correlation_matrix: Mapped[dict] = mapped_column(JSON, default=dict)
    stress_results: Mapped[dict] = mapped_column(JSON, default=dict)
    weights: Mapped[dict] = mapped_column(JSON, default=dict)

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="risk_snapshots"
    )
