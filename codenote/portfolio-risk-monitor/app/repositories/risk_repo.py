import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RiskSnapshot


class RiskSnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, snapshot: RiskSnapshot) -> RiskSnapshot:
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def get_latest(self, portfolio_id: uuid.UUID) -> RiskSnapshot | None:
        stmt = (
            select(RiskSnapshot)
            .where(RiskSnapshot.portfolio_id == portfolio_id)
            .order_by(RiskSnapshot.computed_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_history(
        self,
        portfolio_id: uuid.UUID,
        limit: int = 100,
    ) -> list[RiskSnapshot]:
        stmt = (
            select(RiskSnapshot)
            .where(RiskSnapshot.portfolio_id == portfolio_id)
            .order_by(RiskSnapshot.computed_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_composite_scores(
        self,
        portfolio_id: uuid.UUID,
        limit: int = 20,
    ) -> list[float]:
        stmt = (
            select(RiskSnapshot.composite_score)
            .where(RiskSnapshot.portfolio_id == portfolio_id)
            .order_by(RiskSnapshot.computed_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
