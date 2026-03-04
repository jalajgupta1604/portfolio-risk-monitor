import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession, RiskServiceDep
from app.repositories.portfolio_repo import PortfolioRepository
from app.schemas.payment import TIER_ORDER
from app.schemas.risk import RiskHistoryResponse, RiskReportResponse
from app.services.explanation_service import ExplanationService
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

    user_tier = getattr(current_user, "subscription_tier", "free") or "free"
    user_order = TIER_ORDER.get(user_tier, 0)

    # AI explanation for paid+ users
    if user_order >= TIER_ORDER["paid"]:
        explanation = await ExplanationService.explain(report)
        report.risk_explanation = explanation

    # Strip premium-only fields for non-premium users
    if user_order < TIER_ORDER["premium"]:
        report.macro_sensitivities = None

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
