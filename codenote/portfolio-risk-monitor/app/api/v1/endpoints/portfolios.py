import uuid
from datetime import datetime

from fastapi import APIRouter, Query, status

from app.api.deps import PortfolioServiceDep
from app.schemas.portfolio import (
    BulkPriceUpload,
    HoldingCreate,
    HoldingResponse,
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioUpdate,
)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    data: PortfolioCreate,
    service: PortfolioServiceDep,
) -> PortfolioResponse:
    return await service.create_portfolio(data)


@router.get("", response_model=list[PortfolioSummary])
async def list_portfolios(service: PortfolioServiceDep) -> list[PortfolioSummary]:
    return await service.list_portfolios()


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: uuid.UUID,
    service: PortfolioServiceDep,
) -> PortfolioResponse:
    return await service.get_portfolio(portfolio_id)


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: uuid.UUID,
    data: PortfolioUpdate,
    service: PortfolioServiceDep,
) -> PortfolioResponse:
    return await service.update_portfolio(portfolio_id, data)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: uuid.UUID,
    service: PortfolioServiceDep,
) -> None:
    await service.delete_portfolio(portfolio_id)


@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_holding(
    portfolio_id: uuid.UUID,
    data: HoldingCreate,
    service: PortfolioServiceDep,
) -> HoldingResponse:
    return await service.add_holding(portfolio_id, data)


@router.delete(
    "/{portfolio_id}/holdings/{holding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_holding(
    portfolio_id: uuid.UUID,
    holding_id: uuid.UUID,
    service: PortfolioServiceDep,
) -> None:
    await service.remove_holding(portfolio_id, holding_id)


@router.get("/{portfolio_id}/prices/{symbol}")
async def get_prices(
    portfolio_id: uuid.UUID,
    symbol: str,
    service: PortfolioServiceDep,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> list[dict]:
    return await service.get_price_history(symbol, start_date, end_date)


@router.post("/prices/upload", status_code=status.HTTP_201_CREATED)
async def upload_prices(
    data: BulkPriceUpload,
    service: PortfolioServiceDep,
) -> dict:
    count = await service.upload_prices(data)
    return {"uploaded": count}
