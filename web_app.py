from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from src.chat_bot.core.chat_node import ChatNode
import uuid, json, os

app = FastAPI()
bot = ChatNode()

HISTORY_FILE = "chat_history.json"

# Load or create session histories
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        session_histories = json.load(f)
else:
    session_histories = {}

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(session_histories, f, indent=2)

BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>🤖 Chat-Bot (Gemini)</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background:#f0f2f5;
    margin:0;
    display:flex;
    justify-content:center;
}}
.container {{
    max-width:600px;
    width:100%;
    margin-top:50px;
    background:#fff;
    border-radius:12px;
    box-shadow:0 8px 20px rgba(0,0,0,0.1);
    display:flex;
    flex-direction:column;
    height:80vh;
}}
h2 {{
    text-align:center;
    margin:20px 0;
    color:#333;
}}
.chat-box {{
    flex:1;
    padding:20px;
    overflow-y:auto;
    border-top:1px solid #ddd;
    border-bottom:1px solid #ddd;
}}
.message {{
    padding:12px;
    border-radius:10px;
    margin-bottom:15px;
    max-width:80%;
    word-wrap:break-word;
}}
.user-message {{
    background:#d1e7ff;
    align-self:flex-end;
}}
.bot-message {{
    background:#f0f0f0;
    align-self:flex-start;
}}
form {{
    display:flex;
    padding:10px 20px;
}}
input[name="message"] {{
    flex:1;
    padding:10px;
    border:1px solid #ccc;
    border-radius:6px;
    font-size:16px;
}}
button {{
    padding:10px 20px;
    margin-left:10px;
    border:none;
    background:#4CAF50;
    color:white;
    border-radius:6px;
    cursor:pointer;
}}
button:hover {{ background:#45a049; }}
</style>
</head>
<body>
<div class="container">
<h2>🤖 Chat-Bot (Gemini)</h2>
<div class="chat-box" id="chat-box"></div>
<form id="chat-form">
<input name="message" placeholder="Type your message..." required autofocus />
<button type="submit">Send</button>
</form>
</div>

<script>
const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
let sessionId = localStorage.getItem("session_id") || "";

// Render messages
function addMessage(role, text){{
    const div = document.createElement('div');
    div.className = 'message ' + (role==='user'?'user-message':'bot-message');
    div.innerHTML = `<strong>${{role==='user'?'You':'Bot'}}:</strong> ${{text}}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}}

// Load existing history
async function loadHistory(){{
    if(!sessionId) return;
    const res = await fetch(`/get_history?session_id=${{sessionId}}`);
    const data = await res.json();
    data.history.forEach(([role,text]) => addMessage(role,text));
}}

chatForm.addEventListener('submit', async e => {{
    e.preventDefault();
    const message = chatForm.elements['message'].value.trim();
    if(!message) return;
    addMessage('user', message);
    chatForm.elements['message'].value = '';

    const formData = new FormData();
    formData.append('message', message);
    formData.append('session_id', sessionId);

    const res = await fetch('/send_message', {{
        method:'POST',
        body: formData
    }});
    const data = await res.json();
    addMessage('bot', data.response);
    sessionId = data.session_id;
    localStorage.setItem('session_id', sessionId);
}});

loadHistory();
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return BASE_HTML

@app.get("/get_history")
async def get_history(session_id: str):
    if not session_id or session_id not in session_histories:
        return {"history": []}
    return {"history": session_histories[session_id]}

@app.post("/send_message")
async def send_message(message: str = Form(...), session_id: str = Form(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    if session_id not in session_histories:
        session_histories[session_id] = []
    session_histories[session_id].append(("user", message))
    response_text = bot.chat(message)
    session_histories[session_id].append(("bot", response_text))
    save_history()
    return {"response": response_text, "session_id": session_id}