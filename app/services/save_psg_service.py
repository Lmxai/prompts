import json
import logging
import redis.asyncio as redis

from app.config.config import Config
from app.repositories.mongo_db_repository import MongoDBRepository


class RedisService:
    def __init__(self):
        """
        RedisService constructor.
        """
        self.redis_url = Config.REDIS_URL
        self.backend_url = Config.BACKEND_URL
        self.redis_client = None
        self.mongo_repository = MongoDBRepository()

    async def connect(self):
        """Redis'e bağlanır."""
        try:
            self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
            logging.info(f"Connected to Redis at {self.redis_url}")
        except redis.ConnectionError as e:
            logging.error(f"Redis connection error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during Redis connection: {e}")

    async def close(self):
        """Redis bağlantısını kapatır."""
        if self.redis_client:
            try:
                await self.redis_client.aclose()
                logging.info("Redis connection closed.")
            except Exception as e:
                logging.error(f"Error closing Redis connection: {e}")

    async def write_to_redis(self, session_id: str, chat_data: dict):
        """
        Veriyi Redis'e yazar ve backend endpoint'ini tetikler.
        """
        try:
            if not self.redis_client:
                logging.error("Redis client is not connected. Attempting to reconnect...")
                await self.connect()
                if not self.redis_client:
                    logging.error("Failed to reconnect to Redis.")
                    return

            # Veriyi JSON formatına çevir ve Redis'e yaz
            serialized_data = json.dumps(chat_data, ensure_ascii=False)
            await self.redis_client.set(session_id, serialized_data)
            logging.info(f"Chat data written to Redis for session: {session_id}")

            # Backend endpoint'ini tetikle
            RedisService.trigger_backend(session_id=session_id)
        except redis.RedisError as e:
            logging.error(f"Redis operation failed: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while writing to Redis: {e}")

    @staticmethod
    def trigger_backend(session_id: str):
        """
        Backend endpoint'ini tetiklemek için HTTP isteği gönderir.

        :param session_id: Backend'e gönderilecek session ID
        """
        print("trigger_backend")

    async def save_chat(self, session_id: str, question: str, answer: str):
        """
        MongoDB'ye yazılan veriyi ayrıca Redis'e yazar ve backend'i tetikler.

        :param session_id: Session ID
        :param question: Kullanıcıdan gelen soru
        :param answer: LLM tarafından üretilen cevap
        """
        try:
            # MongoDB'ye yaz
            question_id = await self.mongo_repository.add_new_chat_to_db(
                session_id=session_id,
                question_id=session_id,  # Aynı session_id kullanılabilir
                question=question,
                answer=answer
            )

            if question_id:
                logging.info(f"Chat data saved to MongoDB for session: {session_id}")
                # Redis'e yaz ve backend'i tetikle
                chat_data = {"session_id": session_id, "question": question, "answer": answer}
                await self.write_to_redis(session_id, chat_data)
            else:
                logging.error(f"Failed to save chat data to MongoDB for session: {session_id}")
        except Exception as e:
            logging.error(f"Unexpected error during save_chat: {e}")
