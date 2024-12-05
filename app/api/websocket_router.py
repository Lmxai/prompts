import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.web_socket_connection_manager import ConnectionManager

router = APIRouter(tags=["Web Socket"])

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    - Path: /ws
    - Protocol: WebSocket
    """
    await manager.connect(websocket)
    logging.info("New WebSocket connection established.")
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Message received from client: {data}")
            await manager.broadcast(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.warning("Client disconnected.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

@router.get(
    path="/ws-info",
    summary="WebSocket Endpoint Info",
    description="Provides information about the WebSocket endpoint `/ws`. Use this endpoint for real-time communication.",

)
async def ws_info():
    """
    Swagger'da WebSocket hakkında bilgi veren bir endpoint. Aktif bağlantı sayısını döndürür.
    """
    return {
        "message": "WebSocket status",
        "active_connections": len(manager.active_connections)
    }
