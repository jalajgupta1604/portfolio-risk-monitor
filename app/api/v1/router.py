from fastapi import APIRouter

from app.api.v1.endpoints import auth, brokers, health, payments, portfolios, reports, risk, stocks, ws

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(portfolios.router)
api_router.include_router(risk.router)
api_router.include_router(stocks.router)
api_router.include_router(ws.router)
api_router.include_router(brokers.router)
api_router.include_router(payments.router)
api_router.include_router(reports.router)
