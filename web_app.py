from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from src.chat_bot.core.chat_node import ChatNode
import uuid
import json
import os

app = FastAPI()
bot = ChatNode()

# File to store session histories
HISTORY_FILE = "chat_history.json"

# Load existing history from JSON file
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        session_histories = json.load(f)
else:
    session_histories = {}

# Save history to file
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(session_histories, f, indent=2)

BASE_HTML = """
<html>
<head>
    <title>🤖 Chat-Bot (Gemini)</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; margin:0; padding:0; display:flex; justify-content:center; }}
        .container {{ max-width:600px; width:100%; margin-top:50px; background-color:#fff; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.1); display:flex; flex-direction:column; height:80vh; }}
        h2 {{ text-align:center; color:#333; margin:20px 0; }}
        .chat-box {{ flex:1; overflow-y:auto; padding:20px; }}
        .message {{ padding:12px; border-radius:10px; margin-bottom:15px; max-width:80%; word-wrap:break-word; }}
        .user-message {{ background-color:#d1e7ff; align-self:flex-end; }}
        .bot-message {{ background-color:#f0f0f0; align-self:flex-start; }}
        form {{ display:flex; padding:10px 20px; border-top:1px solid #ddd; }}
        input[name="message"] {{ flex:1; padding:10px; border:1px solid #ccc; border-radius:6px; font-size:16px; }}
        button {{ padding:10px 20px; margin-left:10px; border:none; background-color:#4CAF50; color:white; font-size:16px; border-radius:6px; cursor:pointer; }}
        button:hover {{ background-color:#45a049; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Chat-Bot (Gemini)</h2>
        <div class="chat-box" id="chat-box">
            {chat_history}
        </div>
        <form action="/" method="post">
            <input name="message" placeholder="Type your message here..." required autofocus />
            <button type="submit">Send</button>
        </form>
    </div>
    <script>
        var chatBox = document.getElementById('chat-box');
        chatBox.scrollTop = chatBox.scrollHeight;
    </script>
</body>
</html>
"""

def format_chat(messages):
    html = ""
    for role, msg in messages:
        css_class = "user-message" if role == "user" else "bot-message"
        label = "You" if role == "user" else "Bot"
        html += f'<div class="message {css_class}"><strong>{label}:</strong> {msg}</div>'
    return html

def get_session_id(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, max_age=60*60*24*30)  # 30 days
    return session_id

@app.get("/", response_class=HTMLResponse)
def index(request: Request, response: Response):
    session_id = get_session_id(request, response)
    messages = session_histories.get(session_id, [])
    return BASE_HTML.format(chat_history=format_chat(messages))

@app.post("/", response_class=HTMLResponse)
def chat(request: Request, response: Response, message: str = Form(...)):
    session_id = get_session_id(request, response)
    if session_id not in session_histories:
        session_histories[session_id] = []

    # Add user message
    session_histories[session_id].append(("user", message))
    # Get bot response
    response_text = bot.chat(message)
    session_histories[session_id].append(("bot", response_text))

    # Save to file
    save_history()

    return BASE_HTML.format(chat_history=format_chat(session_histories[session_id]))