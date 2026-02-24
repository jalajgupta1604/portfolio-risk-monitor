from fastapi import APIRouter

from app.api.v1.endpoints import health, portfolios, risk

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(portfolios.router)
api_router.include_router(risk.router)
