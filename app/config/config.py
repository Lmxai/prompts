import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_HOST = os.getenv("MONGO_HOST")
    MONGO_PORT = int(os.getenv("MONGO_PORT"))
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_DB_COLLECTION_NAME = os.getenv("MONGO_DB_COLLECTION_NAME")
    MONGO_DB_PROMPT_COLLECTION_NAME = os.getenv("MONGO_DB_PROMPT_COLLECTION_NAME")

    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
    USER_AGENT = os.getenv("USER_AGENT")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

    CONTEXTUALIZE_Q_SYSTEM_PROMPT = os.getenv("CONTEXTUALIZE_Q_SYSTEM_PROMPT")
    SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
    TOOL_SETUP_PROMPT = os.getenv("TOOL_SETUP_PROMPT")
    PLANNER_PROMPT_TEMPLATE = os.getenv("PLANNER_PROMPT_TEMPLATE")

    REDIS_URL = os.getenv("REDIS_URL")
    BACKEND_URL = os.getenv("BACKEND_URL")