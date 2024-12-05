from app.models import Prompt
from app.repositories.mongo_db_prompts_repository import MongoDBPromptRepository
from app.config.logger import logging
from pymongo.errors import DuplicateKeyError

# PromptService için bir logger oluşturuyoruz
logger = logging.getLogger("PromptService")

class PromptService:
    def __init__(self,db_name: str, collection_name: str):
        """
        PromptService, MongoDBPromptRepository ile çalışır.
        """
        self.repository = MongoDBPromptRepository(db_name=db_name, collection_name=collection_name)

    async def get_all_prompts(self):
        """
        Tüm promptları listele.
        """
        try:
            prompts = await self.repository.list_all_prompts()
            logger.info(f"Successfully fetched {len(prompts)} prompts.")
            return prompts
        except Exception as e:
            logger.error(f"Error fetching all prompts: {e}", exc_info=True)
            raise ValueError(f"Error fetching all prompts: {e}")

    async def get_prompt_by_type(self, prompt_type: str):
        """
        Belirli bir türdeki promptu al.
        """
        try:
            prompt = await self.repository.get_prompt(prompt_type)
            if not prompt:
                logger.warning(f"Prompt type '{prompt_type}' not found.")
                raise ValueError(f"Prompt type '{prompt_type}' not found")
            logger.info(f"Successfully fetched prompt: {prompt_type}")
            return prompt
        except Exception as e:
            logger.error(f"Error fetching prompt by type '{prompt_type}': {e}", exc_info=True)
            raise ValueError(f"Error fetching prompt by type: {e}")

    async def add_prompt(self, prompt_data: dict):
        """
        Yeni bir prompt ekle. Aynı type'a sahip birden fazla prompt eklenebilir.
        """
        try:
            # Gelen veriyi Pydantic modeline dönüştürerek doğrula
            new_prompt = Prompt(**prompt_data)

            # Veritabanına ekle
            await self.repository.add_prompt(
                prompt_type=new_prompt.type,
                template=new_prompt.template,
                placeholders=new_prompt.placeholders,
                description=new_prompt.description,
                is_active=new_prompt.is_active,
                id=new_prompt.id,
                created_at=new_prompt.created_at
            )
            logger.info(f"Successfully added new prompt: {new_prompt.id}")
        except KeyError as e:
            logger.error(f"Missing required field: {e}", exc_info=True)
            raise ValueError(f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"Error adding new prompt: {e}", exc_info=True)
            raise ValueError(f"Error adding new prompt: {e}")

    async def update_prompt(self, prompt_type: str, updated_data: dict):
        """
        Mevcut bir promptu güncelle.
        """
        try:
            existing_prompt = await self.repository.get_prompt(prompt_type)
            if not existing_prompt:
                logger.warning(f"Prompt type '{prompt_type}' not found for update.")
                raise ValueError(f"Prompt type '{prompt_type}' not found")
            await self.repository.update_prompt(
                prompt_type=prompt_type,
                template=updated_data["template"],
                placeholders=updated_data["placeholders"],
                description=updated_data.get("description", "")
            )
            logger.info(f"Successfully updated prompt: {prompt_type}")
        except Exception as e:
            logger.error(f"Error updating prompt '{prompt_type}': {e}", exc_info=True)
            raise ValueError(f"Error updating prompt: {e}")

    async def delete_prompt(self, prompt_type: str):
        """
        Promptu sil.
        """
        try:
            result = await self.repository.delete_prompt(prompt_type)
            if not result:
                logger.warning(f"Prompt type '{prompt_type}' not found for deletion.")
                raise ValueError(f"Prompt type '{prompt_type}' not found")
            logger.info(f"Successfully deleted prompt: {prompt_type}")
        except Exception as e:
            logger.error(f"Error deleting prompt '{prompt_type}': {e}", exc_info=True)
            raise ValueError(f"Error deleting prompt: {e}")
