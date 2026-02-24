"""WebSocket connection manager for live risk updates."""

import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, portfolio_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[portfolio_id].append(websocket)
        logger.info("WS connected: portfolio=%s (total=%d)", portfolio_id, len(self.connections[portfolio_id]))

    def disconnect(self, portfolio_id: str, websocket: WebSocket) -> None:
        clients = self.connections.get(portfolio_id, [])
        if websocket in clients:
            clients.remove(websocket)
        if not clients and portfolio_id in self.connections:
            del self.connections[portfolio_id]
        logger.info("WS disconnected: portfolio=%s", portfolio_id)

    async def broadcast(self, portfolio_id: str, data: dict) -> None:
        clients = self.connections.get(portfolio_id, [])
        disconnected = []
        for ws in clients:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(portfolio_id, ws)
        if clients:
            logger.info("WS broadcast to %d clients for portfolio=%s", len(clients) - len(disconnected), portfolio_id)


manager = ConnectionManager()
