from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from src.chat_bot.core.chat_node import ChatNode
import uuid

app = FastAPI()
bot = ChatNode()

# In-memory session histories
session_histories = {}

def get_session_id(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, max_age=60*60*24*30)
    return session_id

def format_chat(messages):
    html = ""
    for role, msg in messages:
        css_class = "user-message" if role == "user" else "bot-message"
        label = "You" if role == "user" else "Bot"
        html += f'<div class="message {css_class}"><strong>{label}:</strong> {msg}</div>'
    return html

BASE_HTML = """<html>
<head>
<style>
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f5f5f5; display:flex; justify-content:center; margin:0; }}
.container {{ max-width:600px; width:100%; margin-top:50px; background:#fff; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.1); display:flex; flex-direction:column; height:80vh; }}
h2 {{ text-align:center; color:#333; margin:20px 0; }}
.chat-box {{ flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; }}
.message {{ padding:12px; border-radius:10px; margin-bottom:15px; max-width:80%; word-wrap:break-word; }}
.user-message {{ background:#d1e7ff; align-self:flex-end; }}
.bot-message {{ background:#f0f0f0; align-self:flex-start; }}
form {{ display:flex; padding:10px 20px; border-top:1px solid #ddd; }}
input[name="message"] {{ flex:1; padding:10px; border:1px solid #ccc; border-radius:6px; font-size:16px; }}
button {{ padding:10px 20px; margin-left:10px; border:none; background:#4CAF50; color:white; font-size:16px; border-radius:6px; cursor:pointer; }}
button:hover {{ background:#45a049; }}
</style>
</head>
<body>
<div class="container">
<h2>🤖 Chat-Bot (Gemini)</h2>
<div class="chat-box" id="chat-box">{chat_history}</div>
<form id="chat-form">
<input id="message-input" name="message" placeholder="Type your message here..." required autofocus />
<button type="submit">Send</button>
<button type="button" id="clear-btn">Clear Chat</button>
</form>
</div>
<script>
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chatBox = document.getElementById('chat-box');
const clearBtn = document.getElementById('clear-btn');

chatForm.addEventListener('submit', async (e) => {{
    e.preventDefault();
    const message = messageInput.value;
    messageInput.value = '';
    chatBox.innerHTML += `<div class="message user-message"><strong>You:</strong> ${message}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    const formData = new FormData();
    formData.append('message', message);
    const res = await fetch('/api/chat', {{ method: 'POST', body: formData }});
    const html = await res.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const botMessages = doc.querySelectorAll('.bot-message');
    const lastBotMessage = botMessages[botMessages.length - 1];
    if(lastBotMessage) {{
        chatBox.innerHTML += lastBotMessage.outerHTML;
        chatBox.scrollTop = chatBox.scrollHeight;
    }}
}});

clearBtn.addEventListener('click', async () => {{
    const res = await fetch('/api/chat/clear', {{ method: 'POST' }});
    chatBox.innerHTML = '';
}});
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index(request: Request, response: Response):
    session_id = get_session_id(request, response)
    messages = session_histories.get(session_id, [])
    return BASE_HTML.format(chat_history=format_chat(messages))

@app.post("/", response_class=HTMLResponse)
def chat_endpoint(request: Request, response: Response, message: str = Form(...)):
    session_id = get_session_id(request, response)
    if session_id not in session_histories:
        session_histories[session_id] = []

    session_histories[session_id].append(("user", message))
    bot_response = bot.chat(message)
    session_histories[session_id].append(("bot", bot_response))

    return BASE_HTML.format(chat_history=format_chat(session_histories[session_id]))

@app.post("/clear")
def clear_chat(request: Request, response: Response):
    session_id = get_session_id(request, response)
    session_histories[session_id] = []
    return {"status": "cleared"}