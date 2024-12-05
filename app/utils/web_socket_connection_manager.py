import logging
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        """Yeni bir WebSocket bağlantısını kabul eder."""
        await websocket.accept()
        logging.info("WebSocket client connected")
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """WebSocket bağlantısını sonlandırır."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info("WebSocket client disconnected")

    async def send_message(self, websocket: WebSocket, message: str):
        """Belirli bir WebSocket istemcisine mesaj gönderir."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Error sending message to client: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Tüm bağlı istemcilere mesaj gönderir."""
        for connection in self.active_connections:
            await self.send_message(connection, message)

    async def connect_websocket(self):
        """WebSocket bağlantısını manuel olarak başlatır."""
        if not self.active_connections:
            logging.info("Initializing WebSocket connections.")
            # Bağlantı başlatma işlemleri (ör. bir test bağlantısı)


    async def close_connections(self):
        """Tüm WebSocket bağlantılarını kapatır."""
        for connection in self.active_connections:
            await connection.close()
            self.active_connections.remove(connection)
            logging.info("WebSocket connection closed")
