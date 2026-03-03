import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broker import BrokerConnection


class BrokerConnectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: uuid.UUID,
        broker_name: str,
        access_token_encrypted: str | None = None,
        api_key: str | None = None,
        token_expires_at: datetime | None = None,
    ) -> BrokerConnection:
        conn = BrokerConnection(
            user_id=user_id,
            broker_name=broker_name,
            access_token_encrypted=access_token_encrypted,
            api_key=api_key,
            token_expires_at=token_expires_at,
            is_active=True,
        )
        self.session.add(conn)
        await self.session.flush()
        return conn

    async def get_by_id(
        self, connection_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> BrokerConnection | None:
        stmt = select(BrokerConnection).where(BrokerConnection.id == connection_id)
        if user_id is not None:
            stmt = stmt.where(BrokerConnection.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_broker(
        self, user_id: uuid.UUID, broker_name: str
    ) -> BrokerConnection | None:
        stmt = select(BrokerConnection).where(
            BrokerConnection.user_id == user_id,
            BrokerConnection.broker_name == broker_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[BrokerConnection]:
        stmt = (
            select(BrokerConnection)
            .where(BrokerConnection.user_id == user_id)
            .order_by(BrokerConnection.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active_api_connections(
        self, user_id: uuid.UUID
    ) -> list[BrokerConnection]:
        stmt = (
            select(BrokerConnection)
            .where(
                BrokerConnection.user_id == user_id,
                BrokerConnection.is_active == True,  # noqa: E712
                BrokerConnection.access_token_encrypted.isnot(None),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_token(
        self,
        connection: BrokerConnection,
        access_token_encrypted: str,
        token_expires_at: datetime | None = None,
    ) -> BrokerConnection:
        connection.access_token_encrypted = access_token_encrypted
        connection.token_expires_at = token_expires_at
        connection.is_active = True
        await self.session.flush()
        return connection

    async def update_last_synced(self, connection_id: uuid.UUID) -> None:
        stmt = (
            update(BrokerConnection)
            .where(BrokerConnection.id == connection_id)
            .values(last_synced_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def deactivate(self, connection_id: uuid.UUID) -> None:
        stmt = (
            update(BrokerConnection)
            .where(BrokerConnection.id == connection_id)
            .values(is_active=False)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete(self, connection_id: uuid.UUID) -> None:
        conn = await self.get_by_id(connection_id)
        if conn:
            await self.session.delete(conn)
            await self.session.flush()
