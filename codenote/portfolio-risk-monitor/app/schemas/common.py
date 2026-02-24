import uuid
from datetime import datetime

from pydantic import BaseModel


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    id: uuid.UUID


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
