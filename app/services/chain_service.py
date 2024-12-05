from asyncio import sleep
from uuid import uuid4
from datetime import datetime, timezone

from langgraph.graph import END, StateGraph, START

from app.config.config import Config
from app.config.logger import logging
from app.models import QueryRequest, QueryAgentResponse
from app.models.state_model import WorkflowState
from app.repositories.mongo_db_repository import MongoDBRepository

from app.services.llm_service import LLMService
from app.tools.plan_tool import PlanTool
from app.tools.solve_tool import SolveTool
from app.tools.tool_execution import ToolExecution
from app.utils.chat_history_optimizer import ChatHistoryOptimizer
from app.services.save_psg_service import RedisService


class ChainService:
    def __init__(self):
        self._llm_service = None
        self._plan_tool = None
        self._tool_execution = None
        self._solve_tool = None
        self._chat_history_optimizer = None
        self._save_redis = None
        self._mongo_db_repository = None

    @property
    def mongo_db_repository(self):
        if self._mongo_db_repository is None:
            self._mongo_db_repository = MongoDBRepository(db_name=Config.MONGO_DB_NAME,
                                                          collection_name=Config.MONGO_DB_COLLECTION_NAME)
        return self._mongo_db_repository

    @property
    def save_redis(self):
        if self._save_redis is None:
            self._save_redis = RedisService()
        return self._save_redis

    @property
    def llm_service(self):
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service

    @property
    def plan_tool(self):
        if self._plan_tool is None:
            self._plan_tool = PlanTool(self.llm_service)
        return self._plan_tool

    @property
    def tool_execution(self):
        if self._tool_execution is None:
            self._tool_execution = ToolExecution(self.llm_service)
        return self._tool_execution

    @property
    def solve_tool(self):
        if self._solve_tool is None:
            self._solve_tool = SolveTool(self.llm_service)
        return self._solve_tool

    async def execute_workflow(self, query: QueryRequest):
        logging.info("---------------------- Execute Workflow -----------------------")
        question = query.question
        session_id = query.sessionID

        if session_id is None:
            session_id = str(uuid4())
            chat_history_messages = []
        else:
            # Yeni async sınıfa uygun çağrı
            chat_history = await self.mongo_db_repository.get_session_history(session_id=session_id)
            chat_history_messages = ChatHistoryOptimizer.convert_chat_hist_to_messages(chat_history)

            await sleep(5)

        initial_state = WorkflowState(
            task=question,
            messages=chat_history_messages,
            results={},
            steps=[],
            plan_string="",
            prompt_tokens=0,
            completion_tokens=0,
            date=str(datetime.now(timezone.utc))
        )

        result = await self._get_plan(state=initial_state)

        request_result = await self.mongo_db_repository.add_new_chat_to_db(
            session_id=session_id,
            question_id=str(uuid4()),
            question=question,
            answer=result["final_result"]
        )

        await sleep(5)

        await self.save_redis.write_to_redis(session_id=session_id,
                                             chat_data={"question": question,
                                                        "answer": result["final_result"],
                                                        "prompt_tokens": result["prompt_tokens"],
                                                        "completion_tokens": result["completion_tokens"]}
                                             )

        if request_result:
            logging.info(f"Session: {session_id}, Chat saved to MongoDB.")
            logging.info(f"Session: {session_id}, Workflow is completed.")
            logging.info("-------------------------------------------------------------")

            return QueryAgentResponse(session_id=session_id, question=question, answer=result["final_result"],
                                      prompt_tokens=result["prompt_tokens"],
                                      completion_tokens=result["completion_tokens"]), None

        else:
            logging.error(f"Session: {session_id}, Chat could not be saved to MongoDB.")
            return None, {"message": "Failed to save chat to MongoDB."}

    async def _get_plan(self, state: WorkflowState):
        graph = StateGraph(state_schema=WorkflowState)

        graph.add_node("plan", self.plan_tool.run)
        graph.add_node("tool", self.tool_execution.run)
        graph.add_node("solve", self.solve_tool.run)

        graph.add_edge("plan", "tool")
        graph.add_edge("solve", END)
        graph.add_conditional_edges("tool", ChainService._route)
        graph.add_edge(START, "plan")

        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(state)
        return result

    @staticmethod
    def _route(state: WorkflowState):
        total_steps = len(state.steps)
        completed_steps = len(state.completed_steps)

        if completed_steps >= total_steps:
            logging.info("All steps completed, routing to 'solve'.")
            return "solve"
        else:
            logging.info("Not all steps completed, routing to 'tool'.")
            return "tool"
