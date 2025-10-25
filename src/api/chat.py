from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from src.chat_bot.core.chat_node import ChatNode
import uuid
import json
import os

app = FastAPI()
bot = ChatNode()

# File to store session histories
HISTORY_FILE = "chat_history.json"

# Load existing history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        session_histories = json.load(f)
else:
    session_histories = {}

# Save history
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(session_histories, f, indent=2)

@app.post("/api/chat")
async def chat_api(request: Request, message: str = Form(...)):
    # Get session ID from cookies or create new
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in session_histories:
        session_histories[session_id] = []

    # Append user message
    session_histories[session_id].append(("user", message))
    # Get bot response
    response_text = bot.chat(message)
    session_histories[session_id].append(("bot", response_text))

    save_history()

    return JSONResponse({"response": response_text, "session_id": session_id})