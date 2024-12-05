# plan_tool.py
import json
import logging
from datetime import datetime, timezone
from app.models.state_model import WorkflowState
from app.utils.chat_history_optimizer import ChatHistoryOptimizer
from app.utils.get_tokens_from_mesaages import GetMessageTokens
from app.utils.promts import PLANNER_PROMPT


class PlanTool:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.regex_pattern = r"#E\d+"

    async def run(self, state: WorkflowState):
        logging.info("PlanTool is running.")

        if state.messages is None:
            messages = ""
        else:
            messages = ChatHistoryOptimizer.format_chat_history(state.messages)
            logging.info("Chat history optimized.")

        planner_prompt = PLANNER_PROMPT.format(task=state.task, chat_history=messages)

        result = await self.llm_service.invoke(planner_prompt)

        prompt_tokens, completion_tokens = GetMessageTokens.get_tokens_from_messages(message=result)

        # Yanıtı doğrudan state'e ekle
        state.plan_string = result.content
        state.prompt_tokens += prompt_tokens
        state.completion_tokens += completion_tokens
        state.results = {}
        # `plan_string` içindeki adımları `steps` formatında ayrıştırma
        state.steps = PlanTool._parse_steps_from_plan(state.plan_string)

        logging.info("Plan content added to state.")
        logging.info("PlanTool steps: %s", state.steps)

        return state

    @staticmethod
    def _parse_steps_from_plan(plan_string):
        """plan_string'den `steps` yapısını oluşturur."""
        steps = []
        for line in plan_string.splitlines():
            if line.startswith("#E"):
                # Her adımı `(name, tool, input)` formatında ayrıştırıyoruz
                step_id, content = line.split("=", 1)
                step_name = step_id.strip().replace("#", "")
                tool, tool_input = content.strip().split("[", 1)
                tool_input = tool_input.rstrip("]")
                steps.append(
                    (step_name.strip(), tool.strip(), tool_input.strip()))
        return steps
