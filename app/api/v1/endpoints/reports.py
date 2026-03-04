import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DBSession
from app.repositories.portfolio_repo import PortfolioRepository
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{portfolio_id}/weekly")
async def weekly_report(
    portfolio_id: uuid.UUID,
    current_user: CurrentUser,
    session: DBSession,
) -> StreamingResponse:
    # Verify ownership
    repo = PortfolioRepository(session)
    portfolio = await repo.get_by_id(portfolio_id, user_id=current_user.id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    service = ReportService(session)
    try:
        pdf_bytes, filename = await service.generate_weekly_pdf(portfolio_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    from io import BytesIO

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
