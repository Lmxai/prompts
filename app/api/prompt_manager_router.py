from fastapi import APIRouter, HTTPException

from app.config.config import Config
from app.models.prompt_model import Prompt, PromptType
from app.services.prompt_manager_service import PromptService
from pymongo.errors import DuplicateKeyError
from app.config.logger import logging
from typing import List

# Router ve logger
router = APIRouter(tags=["Prompt Management"])
logger = logging.getLogger("PromptManagerRouter")

# PromptService instance


prompt_service = PromptService(db_name=Config.MONGO_DB_NAME, collection_name=Config.MONGO_DB_PROMPT_COLLECTION_NAME)

@router.get(
    "/prompts",
    summary="List all prompts",
    description="Retrieve all the prompts stored in the database.",
    response_model=List[Prompt]
)
async def get_all_prompts():
    """
    Fetch all the available prompts.
    """
    try:
        prompts = await prompt_service.get_all_prompts()
        logger.info("Fetched all prompts successfully.")
        return prompts
    except Exception as e:
        logger.error(f"Error fetching all prompts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while fetching all prompts.")

@router.get(
    "/prompts/{prompt_type}",
    summary="Get a prompt by type",
    description="Retrieve a specific prompt by its type. Valid types are: PLANNER_PROMPT, SOLVER_PROMPT, EXAM_PROMPT.",
    response_model=Prompt
)
async def get_prompt(prompt_type: PromptType):
    """
    Fetch a specific prompt by its type.
    """
    try:
        prompt = await prompt_service.get_prompt_by_type(prompt_type)
        logger.info(f"Fetched prompt successfully: {prompt_type}")
        return prompt
    except ValueError as e:
        logger.warning(f"Prompt type '{prompt_type}' not found.")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching prompt by type '{prompt_type}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while fetching the prompt.")

@router.post(
    "/prompts",
    summary="Add a new prompt",
    description="Add a new prompt to the database. The `type` field must be one of: PLANNER_PROMPT, SOLVER_PROMPT, EXAM_PROMPT.",
    response_model=dict
)
async def add_prompt(prompt: Prompt):
    """
    Add a new prompt.
    """
    try:
        await prompt_service.add_prompt(prompt.dict())
        logger.info(f"Added new prompt successfully: {prompt.type}")
        return {"message": "Prompt added successfully"}
    except DuplicateKeyError as e:
        logger.warning(f"Duplicate prompt type: {prompt.type}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding new prompt '{prompt.type}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while adding the prompt.")

@router.put(
    "/prompts/{prompt_type}",
    summary="Update a prompt",
    description="Update an existing prompt by its type. Valid types are: PLANNER_PROMPT, SOLVER_PROMPT, EXAM_PROMPT.",
    response_model=dict
)
async def update_prompt(prompt_type: PromptType, updated_prompt: Prompt):
    """
    Update an existing prompt.
    """
    try:
        await prompt_service.update_prompt(prompt_type, updated_prompt.dict())
        logger.info(f"Updated prompt successfully: {prompt_type}")
        return {"message": "Prompt updated successfully"}
    except ValueError as e:
        logger.warning(f"Prompt type '{prompt_type}' not found for update.")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating prompt '{prompt_type}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while updating the prompt.")

@router.delete(
    "/prompts/{prompt_type}",
    summary="Delete a prompt",
    description="Delete a specific prompt by its type. Valid types are: PLANNER_PROMPT, SOLVER_PROMPT, EXAM_PROMPT.",
    response_model=dict
)
async def delete_prompt(prompt_type: PromptType):
    """
    Delete a specific prompt by its type.
    """
    try:
        await prompt_service.delete_prompt(prompt_type)
        logger.info(f"Deleted prompt successfully: {prompt_type}")
        return {"message": "Prompt deleted successfully"}
    except ValueError as e:
        logger.warning(f"Prompt type '{prompt_type}' not found for deletion.")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting prompt '{prompt_type}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while deleting the prompt.")
