import logging
from typing import List

from langchain_core.messages import BaseMessage


class ChatHistoryOptimizer:

    @staticmethod
    def filter_chat_history(chat_hist_list: list[str, str], max_characters_per_message=None) -> str:
        if max_characters_per_message is None:
            filtered_chat_history = "\n".join(
                f"\nHuman: {entry['question']['content']}\nAI: {entry['answer']['content']}"
                for entry in chat_hist_list
            )
            logging.info("Filtering chat history.")
            return filtered_chat_history

        else:
            filtered_chat_history = "\n".join(
                f"\nHuman: {entry['question']['content']}\nAI: {entry['answer']['content'][:max_characters_per_message - len(entry['question']['content'])]}"
                for entry in chat_hist_list
                if len(entry['question']['content']) + len(entry['answer']['content']) <= max_characters_per_message
            )
        logging.info("Filtering chat history. Max characters per message: %s", max_characters_per_message)
        return filtered_chat_history

    # todo: request type must be BaseMessage model
    @staticmethod
    def convert_chat_hist_to_messages(chat_hist: List[dict]):
        messages = []
        for message in chat_hist:
            messages.append(BaseMessage(
                type="human",  # İnsan mesajı için type="human"
                role=message["question"]["role"],
                content=message["question"]["content"]
            ))
            messages.append(BaseMessage(
                type="ai",  # Yapay zeka mesajı için type="ai"
                role=message["answer"]["role"],
                content=message["answer"]["content"]
            ))
        return messages

    @staticmethod
    def format_chat_history(messages: List[BaseMessage]) -> str:
        """
        BaseMessage nesnelerinden oluşan bir listeyi string formatına dönüştürür.
        """
        formatted_history = ""
        for message in messages:
            formatted_history += f"{message.role}: {message.content}\n"
        return formatted_history.strip()

