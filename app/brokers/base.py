from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import StringIO


@dataclass
class BrokerHolding:
    symbol: str  # Already normalized to yfinance format (e.g. "RELIANCE.NS")
    quantity: float
    avg_buy_price: float
    current_price: float = 0.0
    sector: str | None = None


class BaseBroker(ABC):
    """Base class for all broker integrations."""

    name: str = ""
    display_name: str = ""
    broker_type: str = ""  # "api" or "csv"

    @abstractmethod
    def supports_api(self) -> bool:
        ...

    @abstractmethod
    def supports_csv(self) -> bool:
        ...


class ApiBroker(BaseBroker):
    """Base class for API-based broker integrations (OAuth + fetch holdings)."""

    broker_type: str = "api"

    def supports_api(self) -> bool:
        return True

    def supports_csv(self) -> bool:
        return False

    @abstractmethod
    def get_login_url(self) -> str:
        ...

    @abstractmethod
    def exchange_token(self, request_token: str) -> dict:
        """Exchange request_token for access_token. Returns dict with access_token, etc."""
        ...

    @abstractmethod
    def fetch_holdings(self, access_token: str) -> list[BrokerHolding]:
        ...


class CsvParser(BaseBroker):
    """Base class for CSV file parsers."""

    broker_type: str = "csv"

    def supports_api(self) -> bool:
        return False

    def supports_csv(self) -> bool:
        return True

    @abstractmethod
    def parse(self, csv_content: StringIO) -> list[BrokerHolding]:
        ...


class PdfParser(BaseBroker):
    """Base class for PDF file parsers (e.g. CAS statements)."""

    broker_type: str = "pdf"

    def supports_api(self) -> bool:
        return False

    def supports_csv(self) -> bool:
        return True  # appears in import modal alongside CSV parsers

    @abstractmethod
    def parse_pdf(self, content: bytes) -> list[BrokerHolding]:
        ...


@dataclass
class BrokerInfo:
    """Metadata about a registered broker integration."""

    name: str
    display_name: str
    broker_type: str  # "api", "csv", or "both"
    supports_api: bool
    supports_csv: bool
