from pydantic import BaseModel, Field


class StockSearchResult(BaseModel):
    symbol: str
    short_name: str = ""
    long_name: str = ""
    exchange: str = ""
    sector: str = ""
    industry: str = ""


class StockSearchResponse(BaseModel):
    query: str
    results: list[StockSearchResult]
    count: int = Field(default=0)


class StockQuote(BaseModel):
    symbol: str
    last_price: float
    previous_close: float
    open: float
    day_high: float
    day_low: float
    change: float
    change_percent: float
