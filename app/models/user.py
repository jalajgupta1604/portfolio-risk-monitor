import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whatsapp_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean, server_default="false", default=False
    )
    subscription_tier: Mapped[str] = mapped_column(
        String(20), server_default="free", default="free"
    )
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    razorpay_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    portfolios: Mapped[list["Portfolio"]] = relationship(  # noqa: F821
        back_populates="owner", lazy="selectin"
    )
    broker_connections: Mapped[list["BrokerConnection"]] = relationship(  # noqa: F821
        back_populates="owner", lazy="selectin"
    )
