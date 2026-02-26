import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def oauth_login(
        self, email: str, full_name: str | None, oauth_provider: str
    ) -> str:
        user = await self._get_by_email(email)
        if user:
            # Link OAuth provider if not already set
            if not user.oauth_provider:
                user.oauth_provider = oauth_provider
                await self.session.flush()
        else:
            user = User(
                email=email,
                full_name=full_name,
                oauth_provider=oauth_provider,
            )
            self.session.add(user)
            await self.session.flush()
        return self._create_token(str(user.id))

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _create_token(user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> str:
        """Verify JWT and return the user_id (sub claim). Raises on invalid token."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            return user_id
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
