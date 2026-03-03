import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BrokerName(str, Enum):
    ZERODHA = "zerodha"
    ZERODHA_CSV = "zerodha_csv"
    GROWW_CSV = "groww_csv"
    CDSL_NSDL = "cdsl_nsdl"


class ImportMode(str, Enum):
    CREATE_NEW = "create_new"
    MERGE_INTO = "merge_into"


class BrokerInfoResponse(BaseModel):
    name: str
    display_name: str
    broker_type: str
    supports_api: bool
    supports_csv: bool


class BrokerListResponse(BaseModel):
    brokers: list[BrokerInfoResponse]


class BrokerConnectionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    broker_name: str
    is_active: bool
    last_synced_at: datetime | None
    created_at: datetime


class BrokerConnectionsListResponse(BaseModel):
    connections: list[BrokerConnectionResponse]


class CsvImportRequest(BaseModel):
    broker: BrokerName = Field(..., description="Which broker's CSV format to parse")
    import_mode: ImportMode = Field(
        ImportMode.CREATE_NEW,
        description="Create new portfolio or merge into existing",
    )
    portfolio_id: uuid.UUID | None = Field(
        None,
        description="Portfolio to merge into (required if import_mode=merge_into)",
    )
    portfolio_name: str | None = Field(
        None,
        description="Name for new portfolio (used if import_mode=create_new)",
    )


class ImportedHoldingSummary(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float
    action: str  # "created" or "updated"


class CsvImportResponse(BaseModel):
    portfolio_id: uuid.UUID
    portfolio_name: str
    total_imported: int
    created: int
    updated: int
    holdings: list[ImportedHoldingSummary]


class ZerodhaLoginUrlResponse(BaseModel):
    login_url: str


class ZerodhaCallbackRequest(BaseModel):
    request_token: str


class SyncResponse(BaseModel):
    broker_name: str
    holdings_synced: int
    portfolio_id: uuid.UUID
    created: int
    updated: int


class AutoSyncResponse(BaseModel):
    synced: list[SyncResponse]
    errors: list[str]
