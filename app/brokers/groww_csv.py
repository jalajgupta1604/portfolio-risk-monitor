import csv
import logging
from io import StringIO

from app.brokers.base import BrokerHolding, CsvParser

logger = logging.getLogger(__name__)

# Groww CSV column name candidates (case-insensitive matching)
_SYMBOL_COLS = {"symbol", "stock symbol", "scrip", "trading symbol", "nse symbol"}
_QTY_COLS = {"quantity", "qty", "shares", "total quantity"}
_AVG_PRICE_COLS = {"avg price", "average price", "buy avg", "buy price", "avg. price", "purchase price"}
_LTP_COLS = {"ltp", "current price", "market price", "last price", "close price", "cur. price"}


def _find_col(headers: list[str], candidates: set[str]) -> int | None:
    for i, h in enumerate(headers):
        if h.strip().lower() in candidates:
            return i
    return None


def _normalize_symbol(symbol: str) -> str:
    """Convert Groww symbol to yfinance format (append .NS if not present)."""
    symbol = symbol.strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    return f"{symbol}.NS"


def _parse_float(value: str) -> float:
    return float(value.strip().replace(",", ""))


class GrowwCsvParser(CsvParser):
    name = "groww_csv"
    display_name = "Groww (CSV Export)"

    def parse(self, csv_content: StringIO) -> list[BrokerHolding]:
        reader = csv.reader(csv_content)
        headers = next(reader, None)
        if not headers:
            raise ValueError("Empty CSV file")

        headers_lower = [h.strip().lower() for h in headers]
        headers = [h.strip() for h in headers]

        sym_idx = _find_col(headers_lower, _SYMBOL_COLS)
        qty_idx = _find_col(headers_lower, _QTY_COLS)
        avg_idx = _find_col(headers_lower, _AVG_PRICE_COLS)
        ltp_idx = _find_col(headers_lower, _LTP_COLS)

        if sym_idx is None or qty_idx is None or avg_idx is None:
            raise ValueError(
                "Could not find required columns (symbol, quantity, avg price) "
                f"in headers: {headers}"
            )

        holdings: list[BrokerHolding] = []
        for row_num, row in enumerate(reader, start=2):
            try:
                if not row or all(c.strip() == "" for c in row):
                    continue
                symbol_raw = row[sym_idx].strip()
                if not symbol_raw:
                    continue
                qty = _parse_float(row[qty_idx])
                if qty <= 0:
                    continue
                avg_price = _parse_float(row[avg_idx])
                ltp = _parse_float(row[ltp_idx]) if ltp_idx is not None else 0.0

                holdings.append(
                    BrokerHolding(
                        symbol=_normalize_symbol(symbol_raw),
                        quantity=qty,
                        avg_buy_price=avg_price,
                        current_price=ltp,
                    )
                )
            except (IndexError, ValueError) as e:
                logger.warning("Skipping row %d in Groww CSV: %s", row_num, e)
                continue

        logger.info("Parsed %d holdings from Groww CSV", len(holdings))
        return holdings
