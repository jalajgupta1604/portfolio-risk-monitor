import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthLogin(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    full_name: str | None = None
    oauth_provider: str = Field(..., min_length=1, max_length=50)


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str | None
    created_at: datetime
    phone_number: str | None = None
    whatsapp_alerts_enabled: bool = False
    subscription_tier: str = "free"
    subscription_expires_at: datetime | None = None


class UserSettingsUpdate(BaseModel):
    phone_number: str | None = None
    whatsapp_alerts_enabled: bool | None = None
