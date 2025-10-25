from src.chat_bot.ai.ai_manager import AIManager
from src.chat_bot.utils.logger import get_logger

logger = get_logger(__name__)

class ChatNode:
    def __init__(self):
        self.ai = AIManager("gemini")

    def chat(self, user_input: str):
        logger.info(f"User: {user_input}")
        response = self.ai.ask(user_input)
        logger.info(f"Bot: {response}")
        return response