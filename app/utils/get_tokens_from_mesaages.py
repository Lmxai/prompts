class GetMessageTokens:
    @staticmethod
    def get_tokens_from_messages(message):
        token_usage = message.response_metadata.get('token_usage', {})
        completion_tokens = token_usage.get('completion_tokens', 0)
        prompt_tokens = token_usage.get('prompt_tokens', 0)

        return completion_tokens, prompt_tokens
