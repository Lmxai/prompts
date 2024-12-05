class BaseAppException(Exception):
    """Tüm uygulama hataları için temel sınıf"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class PromptNotFoundError(BaseAppException):
    """Prompt bulunamadığında kullanılan özel hata."""
    def __init__(self, prompt_type: str):
        self.prompt_type = prompt_type
        self.message = f"No prompt file found for type: {prompt_type}"
        super().__init__(self.message)
