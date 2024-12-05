import logging
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from app.db.mongo_client_manager import MongoClientManager


class MongoDBRepository:
    def __init__(self, db_name: str, collection_name: str):
        self.collection = MongoClientManager.get_database(db_name)[collection_name]

    async def add_new_chat_to_db(self, session_id: str, question_id: str, question: str, answer: str) -> bool:
        message_data = {
            "session_id": session_id,
            "question_id": question_id,
            "simplified": {
                "question": {
                    "role": "human",
                    "content": question
                },
                "answer": {
                    "role": "ai",
                    "content": answer
                }
            },
            "timestamp": datetime.now(timezone.utc)
        }
        try:
            await self.collection.insert_one(message_data)
            return True
        except PyMongoError as e:
            logging.error(f"Error adding message to session: {e}")
            return False

    async def get_session_history(self, session_id: str):
        try:
            cursor = self.collection.find({"session_id": session_id}).sort("timestamp", 1)
            session_data = await cursor.to_list(length=None)
            simplified_data = [item['simplified'] for item in session_data]
            return simplified_data
        except PyMongoError as e:
            logging.error(f"Error fetching session history: {e}")
            return []
