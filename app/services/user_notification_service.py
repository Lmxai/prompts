import logging
from app.utils.web_socket_connection_manager import ConnectionManager


class UserNotificationService:
    manager = ConnectionManager()

    @staticmethod
    async def notify_user(results):
        """
        Kullanıcıya verilen sonuçları WebSocket üzerinden gönderir.
        Args:
            results (list): Gönderilecek mesajların listesi.
        """
        manager = ConnectionManager()
        if not results:
            logging.warning("No results to notify users.")
            return

        for result in results:
            message = f"Snippet: {result.get('snippet', 'No snippet')}, Link: {result.get('link', 'No link')}"
            logging.info(f"Sending message: {message}")
            await manager.broadcast(message=message)
