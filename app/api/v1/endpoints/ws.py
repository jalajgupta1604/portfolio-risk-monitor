import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket import manager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/{portfolio_id}")
async def websocket_endpoint(websocket: WebSocket, portfolio_id: uuid.UUID) -> None:
    pid = str(portfolio_id)
    await manager.connect(pid, websocket)
    try:
        while True:
            # Keep connection alive by waiting for client messages (pings)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(pid, websocket)


@router.post("/notify/{portfolio_id}", include_in_schema=False)
async def notify(portfolio_id: uuid.UUID, body: dict) -> dict:
    """Internal endpoint: broadcast data to all WS clients for a portfolio."""
    await manager.broadcast(str(portfolio_id), body)
    return {"status": "ok"}
