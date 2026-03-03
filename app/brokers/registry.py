import logging

from app.brokers.base import ApiBroker, BaseBroker, BrokerInfo, CsvParser, PdfParser

logger = logging.getLogger(__name__)


class BrokerRegistry:
    """Singleton registry for all broker integrations."""

    _instance: "BrokerRegistry | None" = None
    _brokers: dict[str, BaseBroker]

    def __new__(cls) -> "BrokerRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._brokers = {}
        return cls._instance

    def register(self, broker: BaseBroker) -> None:
        logger.info("Registering broker: %s (%s)", broker.name, broker.broker_type)
        self._brokers[broker.name] = broker

    def get(self, name: str) -> BaseBroker | None:
        return self._brokers.get(name)

    def get_api_broker(self, name: str) -> ApiBroker | None:
        broker = self._brokers.get(name)
        if isinstance(broker, ApiBroker):
            return broker
        return None

    def get_csv_parser(self, name: str) -> CsvParser | None:
        broker = self._brokers.get(name)
        if isinstance(broker, CsvParser):
            return broker
        return None

    def get_pdf_parser(self, name: str) -> PdfParser | None:
        broker = self._brokers.get(name)
        if isinstance(broker, PdfParser):
            return broker
        return None

    def list_all(self) -> list[BrokerInfo]:
        result = []
        for broker in self._brokers.values():
            result.append(
                BrokerInfo(
                    name=broker.name,
                    display_name=broker.display_name,
                    broker_type=broker.broker_type,
                    supports_api=broker.supports_api(),
                    supports_csv=broker.supports_csv(),
                )
            )
        return result

    def list_csv_parsers(self) -> list[BrokerInfo]:
        return [b for b in self.list_all() if b.supports_csv]

    def list_api_brokers(self) -> list[BrokerInfo]:
        return [b for b in self.list_all() if b.supports_api]

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None
