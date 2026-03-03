import csv
import logging
from io import StringIO

from app.brokers.base import BrokerHolding, CsvParser

logger = logging.getLogger(__name__)

# Zerodha Console CSV column name candidates (case-insensitive matching)
_SYMBOL_COLS = {"instrument", "tradingsymbol", "symbol", "stock symbol"}
_QTY_COLS = {"qty.", "qty", "quantity", "net qty", "net qty.", "quantity available"}
_AVG_PRICE_COLS = {"avg. cost", "avg cost", "average price", "avg price", "buy avg", "buy average"}
_LTP_COLS = {"ltp", "cur. val", "current value", "last price", "close price", "previous closing price"}
_EXCHANGE_COLS = {"exchange"}
_SECTOR_COLS = {"sector"}


def _find_col(headers: list[str], candidates: set[str]) -> int | None:
    """Find the first matching column index (case-insensitive)."""
    for i, h in enumerate(headers):
        if h.strip().lower() in candidates:
            return i
    return None


def _normalize_symbol(symbol: str, exchange: str | None) -> str:
    """Convert Zerodha tradingsymbol to yfinance format."""
    symbol = symbol.strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    if exchange and exchange.strip().upper() == "BSE":
        return f"{symbol}.BO"
    return f"{symbol}.NS"


def _parse_float(value: str) -> float:
    """Parse a float value, stripping commas and whitespace."""
    return float(value.strip().replace(",", ""))


class ZerodhaCsvParser(CsvParser):
    name = "zerodha_csv"
    display_name = "Zerodha (CSV Export)"

    def parse(self, csv_content: StringIO) -> list[BrokerHolding]:
        reader = csv.reader(csv_content)
        headers = next(reader, None)
        if not headers:
            raise ValueError("Empty CSV file")

        # Normalize headers
        headers_lower = [h.strip().lower() for h in headers]
        headers = [h.strip() for h in headers]

        sym_idx = _find_col(headers_lower, _SYMBOL_COLS)
        qty_idx = _find_col(headers_lower, _QTY_COLS)
        avg_idx = _find_col(headers_lower, _AVG_PRICE_COLS)
        ltp_idx = _find_col(headers_lower, _LTP_COLS)
        exch_idx = _find_col(headers_lower, _EXCHANGE_COLS)
        sector_idx = _find_col(headers_lower, _SECTOR_COLS)

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
                exchange = row[exch_idx].strip() if exch_idx is not None else None
                sector = row[sector_idx].strip() if sector_idx is not None and sector_idx < len(row) and row[sector_idx].strip() else None

                holdings.append(
                    BrokerHolding(
                        symbol=_normalize_symbol(symbol_raw, exchange),
                        quantity=qty,
                        avg_buy_price=avg_price,
                        current_price=ltp,
                        sector=sector,
                    )
                )
            except (IndexError, ValueError) as e:
                logger.warning("Skipping row %d in Zerodha CSV: %s", row_num, e)
                continue

        logger.info("Parsed %d holdings from Zerodha CSV", len(holdings))
        return holdings
