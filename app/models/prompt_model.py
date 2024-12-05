from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import uuid


class PromptType(str, Enum):
    PLANNER = "PLANNER_PROMPT"
    SOLVER = "SOLVER_PROMPT"
    EXAM = "EXAM_PROMPT"


class Prompt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: PromptType
    template: str
    placeholders: List[str]
    description: str = ""
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
