from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser
from app.schemas.stock import StockQuote, StockSearchResponse
from app.services.stock_service import StockService

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/search", response_model=StockSearchResponse)
async def search_stocks(
    _user: CurrentUser,
    q: str = Query(..., min_length=2, description="Search query"),
    max_results: int = Query(10, ge=1, le=25),
) -> StockSearchResponse:
    results = await StockService.search(q, max_results=max_results)
    return StockSearchResponse(query=q, results=results, count=len(results))


@router.get("/{symbol}/quote", response_model=StockQuote)
async def get_stock_quote(
    _user: CurrentUser,
    symbol: str,
) -> StockQuote:
    try:
        return await StockService.get_quote(symbol)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch quote for {symbol}: {exc}",
        )
