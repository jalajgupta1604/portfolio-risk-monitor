import uuid

from fastapi import APIRouter, Query

from app.api.deps import RiskServiceDep
from app.schemas.risk import RiskHistoryResponse, RiskReportResponse

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/{portfolio_id}/compute", response_model=RiskReportResponse)
async def compute_risk(
    portfolio_id: uuid.UUID,
    service: RiskServiceDep,
) -> RiskReportResponse:
    return await service.compute_risk(portfolio_id)


@router.get("/{portfolio_id}/history", response_model=RiskHistoryResponse)
async def risk_history(
    portfolio_id: uuid.UUID,
    service: RiskServiceDep,
    limit: int = Query(100, ge=1, le=1000),
) -> RiskHistoryResponse:
    return await service.get_risk_history(portfolio_id, limit)
