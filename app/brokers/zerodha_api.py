import logging

from kiteconnect import KiteConnect

from app.brokers.base import ApiBroker, BrokerHolding
from app.config import settings

logger = logging.getLogger(__name__)


def _normalize_symbol(tradingsymbol: str, exchange: str) -> str:
    """Convert Zerodha tradingsymbol to yfinance format (.NS suffix for NSE)."""
    if exchange == "NSE":
        return f"{tradingsymbol}.NS"
    if exchange == "BSE":
        return f"{tradingsymbol}.BO"
    return tradingsymbol


class ZerodhaApiBroker(ApiBroker):
    name = "zerodha"
    display_name = "Zerodha (Kite Connect)"

    def __init__(self) -> None:
        self.api_key = settings.KITE_API_KEY
        self.api_secret = settings.KITE_API_SECRET
        self.redirect_url = settings.KITE_REDIRECT_URL

    def get_login_url(self) -> str:
        kite = KiteConnect(api_key=self.api_key)
        return kite.login_url()

    def exchange_token(self, request_token: str) -> dict:
        kite = KiteConnect(api_key=self.api_key)
        data = kite.generate_session(request_token, api_secret=self.api_secret)
        return {
            "access_token": data["access_token"],
            "user_id": data.get("user_id", ""),
        }

    def fetch_holdings(self, access_token: str) -> list[BrokerHolding]:
        kite = KiteConnect(api_key=self.api_key)
        kite.set_access_token(access_token)
        raw = kite.holdings()
        holdings: list[BrokerHolding] = []
        for item in raw:
            qty = item.get("quantity", 0)
            if qty <= 0:
                continue
            symbol = _normalize_symbol(
                item.get("tradingsymbol", ""),
                item.get("exchange", "NSE"),
            )
            holdings.append(
                BrokerHolding(
                    symbol=symbol,
                    quantity=float(qty),
                    avg_buy_price=float(item.get("average_price", 0)),
                    current_price=float(item.get("last_price", 0)),
                )
            )
        logger.info("Fetched %d holdings from Zerodha API", len(holdings))
        return holdings
