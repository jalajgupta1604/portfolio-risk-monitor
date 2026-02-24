import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession, RiskServiceDep
from app.repositories.portfolio_repo import PortfolioRepository
from app.schemas.risk import RiskHistoryResponse, RiskReportResponse
from app.websocket import manager

router = APIRouter(prefix="/risk", tags=["risk"])


async def _verify_ownership(
    portfolio_id: uuid.UUID, user_id: uuid.UUID, session: DBSession
) -> None:
    repo = PortfolioRepository(session)
    portfolio = await repo.get_by_id(portfolio_id, user_id=user_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )


@router.post("/{portfolio_id}/compute", response_model=RiskReportResponse)
async def compute_risk(
    portfolio_id: uuid.UUID,
    service: RiskServiceDep,
    current_user: CurrentUser,
    session: DBSession,
) -> RiskReportResponse:
    await _verify_ownership(portfolio_id, current_user.id, session)
    report = await service.compute_risk(portfolio_id)
    # Broadcast to WebSocket clients
    await manager.broadcast(str(portfolio_id), report.model_dump(mode="json"))
    return report


@router.get("/{portfolio_id}/history", response_model=RiskHistoryResponse)
async def risk_history(
    portfolio_id: uuid.UUID,
    service: RiskServiceDep,
    current_user: CurrentUser,
    session: DBSession,
    limit: int = Query(100, ge=1, le=1000),
) -> RiskHistoryResponse:
    await _verify_ownership(portfolio_id, current_user.id, session)
    return await service.get_risk_history(portfolio_id, limit)
