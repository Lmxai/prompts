import os
import logging
import json

from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from app.config.config import Config


class LLMService:
    def __init__(self):
        # Çevresel değişkenleri kontrol edin
        langsmith_api_key = Config.LANGCHAIN_API_KEY
        openai_api_key = Config.OPENAI_API_KEY
        if not langsmith_api_key or not openai_api_key:
            logging.error("Environment variables LANGCHAIN_API_KEY and OPENAI_API_KEY must be set.")
            raise ValueError("Environment variables LANGCHAIN_API_KEY and OPENAI_API_KEY must be set.")

        # Log yapılandırması

        # Model adı .env'den alma ve loglama
        try:
            logging.info("--- Setting model name for LLM--- [Step 4]")
            self.model_name = Config.LLM_MODEL_NAME
            logging.info(f"--- Model name set to {self.model_name} [Step 4]")
        except Exception as e:
            logging.error(f"--- Failed to set model name for LLM: {str(e)} [Step 4]")

        # CallbackManager ve tracer ayarları
        tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT", "default_project"))
        callback_manager = CallbackManager([tracer])

        # LLM başlatma
        try:
            logging.info("--- Initializing ChatOpenAI--- [Step 5]")
            self.llm = ChatOpenAI(api_key=openai_api_key, model_name=self.model_name, callbacks=callback_manager)
            logging.info("--- ChatOpenAI initialized successfully. [Step 5]")
        except Exception as e:
            logging.error(f"--- Failed to initialize ChatOpenAI: {str(e)} [Step 5]")

    async def invoke(self, prompt):
        """
        Verilen planner_prompt'u kullanarak bir planner nesnesi oluşturur ve çalıştırır.
        """
        try:
            # Prompt şablonunu oluştur
            prompt_template = [{"role": "user", "content": prompt}]

            # Planner'ı çalıştır ve sonucu al
            #result = await self.llm.ainvoke(prompt_template.format_messages())
            result = await self.llm.ainvoke(prompt_template)
            return result
        except Exception as e:
            logging.error(f"--- Failed to create planner or execute prompt: {str(e)}")
            return "Failed to create planner or execute prompt: {str(e)}"


    async def invoke_solve(self,final_prompt):
        try:
            formatted_prompt = [{"role": "user", "content": final_prompt}]

            result = await self.llm.ainvoke(formatted_prompt)
            return result
        except Exception as e:
            logging.error(f"Error in LLM invoke: {str(e)}")
            raise ValueError(f"Failed to invoke LLM: {str(e)}")

