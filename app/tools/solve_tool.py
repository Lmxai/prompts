import json
import logging
from app.models.state_model import WorkflowState
from app.utils.chat_history_optimizer import ChatHistoryOptimizer
from app.utils.get_tokens_from_mesaages import GetMessageTokens
from app.utils.promts import SOLVE_PROMPT


class SolveTool:
    def __init__(self, llm_service):
        self.llm_service = llm_service

        self.MAX_CHARACTERS = 3000

    async def run(self, state: WorkflowState):
        """
        SolveTool'un ana çalışma fonksiyonu. WorkflowState üzerinde işlem yapar.
        """
        logging.info("SolveTool is running.")

        for key, value in state.results.items():
            result_value = value
            state.final_plan += self._flat_and_clean(result_value) + "\n"

        if state.messages is None:
            messages = ""
        else:
            messages = ChatHistoryOptimizer.format_chat_history(state.messages)

        final_prompt = SOLVE_PROMPT.format(
            task=state.task, plan=state.final_plan, chat_history=messages)

        # logging.info("Prompting solver with the following prompt:\n\n%s", final_prompt)

        result = await self.llm_service.invoke_solve(final_prompt=final_prompt)

        prompt_tokens, completion_tokens = GetMessageTokens.get_tokens_from_messages(message=result)

        state.prompt_tokens += prompt_tokens
        state.completion_tokens += completion_tokens

        # Sonucu kaydet
        state.final_result = result.content
        logging.info(f"SolveTool is completed.")
        logging.info(f"Prompt tokens: {state.prompt_tokens}")
        logging.info(f"Completion tokens: {state.completion_tokens}")

        return state

    def _flat_and_clean(self, data):
        """
        Verilen herhangi bir veri yapısını düz bir metne dönüştürür ve temizler.
        Recursive olmayan bir yöntemle veriyi işler.

        Args:
            data (any): İşlenecek veri (list, dict, str veya başka bir veri yapısı).

        Returns:
            str: Temizlenmiş ve düzleştirilmiş metin.
        """
        flat_text = ""
        stack = [data]  # Verileri işlemek için bir yığın kullanıyoruz

        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                # Sözlük içeriğini stack'e ekle
                stack.extend(current.values())
            elif isinstance(current, list):
                # Liste içeriğini stack'e ekle
                stack.extend(current)
            else:
                # Düz metin ise temizleyip ekle
                cleaned = SolveTool._clean_text(current)
                if len(flat_text) + len(cleaned) <= self.MAX_CHARACTERS:
                    flat_text += cleaned + " "
                else:
                    flat_text += cleaned[:self.MAX_CHARACTERS - len(flat_text)]
                    break

        return flat_text.strip()

    @staticmethod
    def _clean_text(text):
        """
        Metni temizler: Nokta, satır sonu ve çift boşlukları kaldırır.

        Args:
            text (str): Temizlenecek metin.

        Returns:
            str: Temizlenmiş metin.
        """
        return str(text).replace("...", "").replace("\n", "").replace("  ", " ").strip()
