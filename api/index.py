from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from src.chat_bot.core.chat_node import ChatNode
import uuid, json, os

app = FastAPI()
bot = ChatNode()

HISTORY_FILE = "chat_history.json"

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
body {{ font-family: Arial; background:#f5f5f5; margin:0; display:flex; justify-content:center; }}
.container {{ max-width:600px; width:100%; margin-top:50px; background:#fff; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.1); display:flex; flex-direction:column; height:80vh; }}
h2 {{ text-align:center; margin:20px 0; }}
.chat-box {{ flex:1; overflow-y:auto; padding:20px; }}
.message {{ padding:12px; border-radius:10px; margin-bottom:15px; max-width:80%; word-wrap:break-word; }}
.user-message {{ background:#d1e7ff; align-self:flex-end; }}
.bot-message {{ background:#f0f0f0; align-self:flex-start; }}
form {{ display:flex; padding:10px 20px; border-top:1px solid #ddd; }}
input[name="message"] {{ flex:1; padding:10px; border:1px solid #ccc; border-radius:6px; font-size:16px; }}
button {{ padding:10px 20px; margin-left:10px; border:none; background:#4CAF50; color:white; border-radius:6px; cursor:pointer; }}
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

function addMessage(role,text){{
  const div=document.createElement('div');
  div.className='message '+(role==='user'?'user-message':'bot-message');
  div.innerHTML=`<strong>${{role==='user'?'You':'Bot'}}:</strong> ${{text}}`;
  chatBox.appendChild(div);
  chatBox.scrollTop=chatBox.scrollHeight;
}}

chatForm.addEventListener('submit', async e=>{{
  e.preventDefault();
  const message = chatForm.elements['message'].value.trim();
  if(!message) return;
  addMessage('user',message);
  chatForm.elements['message'].value='';
  const formData=new FormData();
  formData.append('message',message);
  const res=await fetch('/api',{{method:'POST',body:formData}});
  const data=await res.json();
  addMessage('bot',data.response);
  sessionId=data.session_id;
  localStorage.setItem('session_id',sessionId);
}});
</script>
</body>
</html>
"""

def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return BASE_HTML

@app.post("/", response_class=JSONResponse)
async def chat_api(request: Request, message: str = Form(...)):
    session_id = get_session_id(request)
    if session_id not in session_histories:
        session_histories[session_id] = []
    session_histories[session_id].append(("user", message))
    response_text = bot.chat(message)
    session_histories[session_id].append(("bot", response_text))
    save_history()
    return {"response": response_text, "session_id": session_id}