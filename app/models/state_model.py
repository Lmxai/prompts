from typing import TypedDict, Optional, List, Dict, Set
from pydantic import BaseModel
import typing_extensions

from dataclasses import dataclass, field

from langchain_core.messages import BaseMessage


@dataclass
class WorkflowState:
    messages: Optional[List[BaseMessage]] = None
    index_name: Optional[str] = None
    steps: List[tuple] = field(default_factory=list)
    plan_string: str = ""
    task: str = ""
    math_results: Optional[Dict[str, str]] = None
    results: Dict[str, str] = field(default_factory=dict)
    date: str = ""
    executed_tools: Set[str] = field(default_factory=set)
    completed_steps: Set[str] = field(default_factory=set)
    final_result: str = ""
    final_plan: str = ""
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0
