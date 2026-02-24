import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StressScenario(BaseModel):
    shock_pct: float
    portfolio_impact_pct: float
    estimated_loss: float


class CorrelationEntry(BaseModel):
    asset_a: str
    asset_b: str
    correlation: float


class RiskReportResponse(BaseModel):
    portfolio_id: uuid.UUID
    computed_at: datetime
    rolling_volatility: float = Field(..., description="Annualized 30D rolling volatility")
    portfolio_beta: float = Field(..., description="Beta vs NIFTY 50")
    downside_beta: float = Field(..., description="Downside beta vs NIFTY 50")
    var_95: float = Field(..., description="95% Value at Risk (daily)")
    var_95_amount: float = Field(..., description="VaR in absolute currency terms")
    composite_score: float = Field(..., ge=0, le=100, description="Composite risk score 0-100")
    risk_level: RiskLevel
    risk_acceleration: float = Field(..., description="Rate of change in composite score")
    correlation_matrix: dict[str, dict[str, float]]
    stress_results: list[StressScenario]
    weights: dict[str, float]
    total_portfolio_value: float
    early_warning_signals: list[str]


class RiskHistoryEntry(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    computed_at: datetime
    composite_score: float
    risk_level: str
    rolling_volatility: float
    var_95: float
    portfolio_beta: float
    risk_acceleration: float


class RiskHistoryResponse(BaseModel):
    portfolio_id: uuid.UUID
    entries: list[RiskHistoryEntry]
    count: int
