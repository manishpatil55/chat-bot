from src.chat_bot.ai.ai_manager import AIManager
from src.chat_bot.utils.logger import get_logger

logger = get_logger(__name__)

class ChatNode:
    def __init__(self):
        self.ai = AIManager("gemini")
        self.history = []  # Store conversation context

    def chat(self, user_input: str):
        # Append user message to history
        self.history.append(("User", user_input))

        # Build conversation context
        context_prompt = ""
        for role, msg in self.history:
            context_prompt += f"{role}: {msg}\n"
        context_prompt += "Bot:"

        # Ask Gemini
        response = self.ai.ask(context_prompt)

        # Store bot response in history
        self.history.append(("Bot", response))

        logger.info(f"User: {user_input}")
        logger.info(f"Bot: {response}")
        return response