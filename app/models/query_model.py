from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from app.config.config import Config


# Backend den gelen veri
class QueryRequest(BaseModel):
    userID: str = Field(..., description="User ID")
    question: str = Field(..., description="User question")
    sessionID: Optional[str] = Field(None, description="Session ID")
    index_name: Optional[str] = None


class QueryAgentResponse(BaseModel):
    answer: str
    session_id: str
    question: str
    response_model_name: str = str(Config.LLM_MODEL_NAME)
    prompt_tokens: int
    completion_tokens: int
