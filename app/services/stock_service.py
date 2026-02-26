import asyncio
from functools import partial

import yfinance as yf

from app.schemas.stock import StockQuote, StockSearchResult


class StockService:
    """Stateless service for searching NSE stocks and fetching quotes via yfinance."""

    @staticmethod
    async def search(query: str, max_results: int = 10) -> list[StockSearchResult]:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, partial(StockService._search_sync, query, max_results)
        )
        return results

    @staticmethod
    def _search_sync(query: str, max_results: int) -> list[StockSearchResult]:
        try:
            search = yf.Search(query, max_results=max_results)
            quotes = getattr(search, "quotes", []) or []
        except Exception:
            return []

        nse_results: list[StockSearchResult] = []
        for q in quotes:
            symbol = q.get("symbol", "")
            exchange = q.get("exchange", "")
            # Filter to NSE equities only (.NS suffix or NSI exchange)
            if not (symbol.endswith(".NS") or exchange in ("NSI", "NSE")):
                continue
            nse_results.append(
                StockSearchResult(
                    symbol=symbol,
                    short_name=q.get("shortname", q.get("shortName", "")),
                    long_name=q.get("longname", q.get("longName", "")),
                    exchange=exchange,
                    sector=q.get("sector", ""),
                    industry=q.get("industry", ""),
                )
            )
        return nse_results[:max_results]

    @staticmethod
    async def get_quote(symbol: str) -> StockQuote:
        loop = asyncio.get_event_loop()
        quote = await loop.run_in_executor(
            None, partial(StockService._get_quote_sync, symbol)
        )
        return quote

    @staticmethod
    def _get_quote_sync(symbol: str) -> StockQuote:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info

        last_price = float(info.get("lastPrice", 0) if isinstance(info, dict) else getattr(info, "last_price", 0))
        previous_close = float(info.get("previousClose", 0) if isinstance(info, dict) else getattr(info, "previous_close", 0))
        open_price = float(info.get("open", 0) if isinstance(info, dict) else getattr(info, "open", 0))
        day_high = float(info.get("dayHigh", 0) if isinstance(info, dict) else getattr(info, "day_high", 0))
        day_low = float(info.get("dayLow", 0) if isinstance(info, dict) else getattr(info, "day_low", 0))

        change = last_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0.0

        return StockQuote(
            symbol=symbol,
            last_price=round(last_price, 2),
            previous_close=round(previous_close, 2),
            open=round(open_price, 2),
            day_high=round(day_high, 2),
            day_low=round(day_low, 2),
            change=round(change, 2),
            change_percent=round(change_percent, 2),
        )
