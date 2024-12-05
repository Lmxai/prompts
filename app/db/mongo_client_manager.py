# app/db/mongo_client_manager.py

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.config import Config


class MongoClientManager:
    _client = None

    @staticmethod
    def get_client():
        if MongoClientManager._client is None:
            try:
                logging.info("Initializing MongoDB client...")
                MongoClientManager._client = AsyncIOMotorClient(Config.MONGO_URI)
            except Exception as e:
                logging.error(f"Error initializing MongoDB client: {e}")
                raise
        return MongoClientManager._client

    @staticmethod
    def get_database(db_name: str):
        client = MongoClientManager.get_client()
        return client[db_name]
