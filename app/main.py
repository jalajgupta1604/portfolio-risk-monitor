import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def _register_brokers() -> None:
    """Register available broker integrations at startup."""
    from app.brokers import BrokerRegistry, CasPdfParser, GrowwCsvParser, ZerodhaCsvParser

    registry = BrokerRegistry()

    # CSV / PDF parsers are always available
    registry.register(ZerodhaCsvParser())
    registry.register(GrowwCsvParser())
    registry.register(CasPdfParser())

    # Zerodha API only if credentials are configured
    if settings.KITE_API_KEY:
        from app.brokers import ZerodhaApiBroker

        registry.register(ZerodhaApiBroker())
        logger.info("Zerodha Kite Connect API broker registered")
    else:
        logger.info("Zerodha API not configured (KITE_API_KEY not set)")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s", settings.APP_NAME)
    _register_brokers()
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Real-time portfolio risk monitoring with collapse early warning signals",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
