import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HoldingCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, examples=["RELIANCE.NS"])
    quantity: float = Field(..., gt=0, examples=[100.0])
    avg_buy_price: float = Field(..., gt=0, examples=[2450.50])
    current_price: float | None = Field(None, ge=0, examples=[2500.00])


class HoldingUpdate(BaseModel):
    quantity: float | None = Field(None, gt=0)
    avg_buy_price: float | None = Field(None, gt=0)
    current_price: float | None = Field(None, ge=0)


class HoldingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    symbol: str
    quantity: float
    avg_buy_price: float
    current_price: float
    market_value: float = 0.0


class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["My Growth Portfolio"])
    description: str | None = Field(None, max_length=1000)
    holdings: list[HoldingCreate] = Field(default_factory=list)


class PortfolioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class PortfolioResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    holdings: list[HoldingResponse]
    total_value: float = 0.0


class PortfolioSummary(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    holdings_count: int = 0
    total_value: float = 0.0


class PriceHistoryCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    date: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(default=0.0, ge=0)


class BulkPriceUpload(BaseModel):
    prices: list[PriceHistoryCreate] = Field(..., min_length=1)
