import uuid

from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import BrokerServiceDep, CurrentUser
from app.schemas.broker import (
    AutoSyncResponse,
    BrokerConnectionResponse,
    BrokerConnectionsListResponse,
    BrokerListResponse,
    CsvImportResponse,
    ImportMode,
    SyncResponse,
    ZerodhaCallbackRequest,
    ZerodhaLoginUrlResponse,
)

router = APIRouter(prefix="/brokers", tags=["brokers"])


@router.get("/available", response_model=BrokerListResponse)
def list_available_brokers(service: BrokerServiceDep) -> BrokerListResponse:
    return service.list_available_brokers()


@router.get("/connections", response_model=BrokerConnectionsListResponse)
async def list_connections(
    service: BrokerServiceDep, user: CurrentUser
) -> BrokerConnectionsListResponse:
    return await service.list_connections(user.id)


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: uuid.UUID, service: BrokerServiceDep, user: CurrentUser
) -> None:
    await service.delete_connection(connection_id, user.id)


@router.get("/zerodha/login-url", response_model=ZerodhaLoginUrlResponse)
def get_zerodha_login_url(service: BrokerServiceDep) -> ZerodhaLoginUrlResponse:
    return service.get_zerodha_login_url()


@router.post("/zerodha/callback", response_model=BrokerConnectionResponse)
async def zerodha_callback(
    body: ZerodhaCallbackRequest, service: BrokerServiceDep, user: CurrentUser
) -> BrokerConnectionResponse:
    return await service.handle_zerodha_callback(body.request_token, user.id)


@router.post("/csv-import", response_model=CsvImportResponse)
async def csv_import(
    service: BrokerServiceDep,
    user: CurrentUser,
    file: UploadFile = File(...),
    broker: str = Form(...),
    import_mode: ImportMode = Form(ImportMode.CREATE_NEW),
    portfolio_id: str | None = Form(None),
    portfolio_name: str | None = Form(None),
) -> CsvImportResponse:
    raw_content = await file.read()
    pid = uuid.UUID(portfolio_id) if portfolio_id else None
    return await service.import_holdings_file(
        user_id=user.id,
        broker_name=broker,
        import_mode=import_mode,
        raw_content=raw_content,
        portfolio_id=pid,
        portfolio_name=portfolio_name,
    )


@router.post("/connections/{connection_id}/sync", response_model=SyncResponse)
async def sync_connection(
    connection_id: uuid.UUID, service: BrokerServiceDep, user: CurrentUser
) -> SyncResponse:
    return await service.sync_connection(connection_id, user.id)


@router.post("/auto-sync", response_model=AutoSyncResponse)
async def auto_sync(
    service: BrokerServiceDep, user: CurrentUser
) -> AutoSyncResponse:
    return await service.auto_sync_all(user.id)
