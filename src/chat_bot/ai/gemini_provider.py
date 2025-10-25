import google.generativeai as genai
from src.chat_bot.config import GEMINI_API_KEY, GEMINI_MODEL
from src.chat_bot.utils.logger import get_logger

logger = get_logger(__name__)

class GeminiProvider:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"GeminiProvider initialized with model {GEMINI_MODEL}")

    def generate_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return "Error: Could not get response from Gemini API."