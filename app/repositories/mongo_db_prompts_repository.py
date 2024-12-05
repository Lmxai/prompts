import logging
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from app.db.mongo_client_manager import MongoClientManager


class MongoDBPromptRepository:
    def __init__(self, db_name: str, collection_name: str):
        self.collection = MongoClientManager.get_database(db_name)[collection_name]

    async def add_prompt(self, prompt_type: str, template: str, placeholders: list, description: str):
        prompt_data = {
            "type": prompt_type,
            "template": template,
            "placeholders": placeholders,
            "description": description,
            "created_at": datetime.now(timezone.utc)
        }
        try:
            await self.collection.insert_one(prompt_data)
            logging.info(f"Prompt added successfully: {prompt_type}")
            return True
        except PyMongoError as e:
            logging.error(f"Error adding prompt: {e}")
            return False

    async def get_prompt(self, prompt_type: str):
        try:
            prompt = await self.collection.find_one({"type": prompt_type}, {"_id": 0})
            if not prompt:
                logging.warning(f"Prompt not found: {prompt_type}")
                return None
            return prompt
        except PyMongoError as e:
            logging.error(f"Error fetching prompt: {e}")
            return None

    async def update_prompt(self, prompt_type: str, template: str, placeholders: list, description: str):
        update_data = {
            "template": template,
            "placeholders": placeholders,
            "description": description,
            "updated_at": datetime.now(timezone.utc)
        }
        try:
            result = await self.collection.update_one({"type": prompt_type}, {"$set": update_data})
            if result.matched_count == 0:
                logging.warning(f"Prompt not found for update: {prompt_type}")
                return False
            logging.info(f"Prompt updated successfully: {prompt_type}")
            return True
        except PyMongoError as e:
            logging.error(f"Error updating prompt: {e}")
            return False

    async def delete_prompt(self, prompt_type: str):
        try:
            result = await self.collection.delete_one({"type": prompt_type})
            if result.deleted_count == 0:
                logging.warning(f"Prompt not found for deletion: {prompt_type}")
                return False
            logging.info(f"Prompt deleted successfully: {prompt_type}")
            return True
        except PyMongoError as e:
            logging.error(f"Error deleting prompt: {e}")
            return False

    async def list_all_prompts(self):
        try:
            prompts = await self.collection.find({}, {"_id": 0}).to_list(length=None)
            logging.info("Fetched all prompts successfully.")
            return prompts
        except PyMongoError as e:
            logging.error(f"Error listing prompts: {e}")
            return []
