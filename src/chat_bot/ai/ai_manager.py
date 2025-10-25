from src.chat_bot.ai.gemini_provider import GeminiProvider

class AIManager:
    def __init__(self, provider="gemini"):
        if provider == "gemini":
            self.provider = GeminiProvider()
        else:
            raise ValueError("Only Gemini is supported right now.")

    def ask(self, prompt):
        return self.provider.generate_response(prompt)