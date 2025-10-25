from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from src.chat_bot.core.chat_node import ChatNode

app = FastAPI()
bot = ChatNode()
chat_history = []

CLEAR_COMMANDS = ["clear", "clear chat", "clear this chat", "reset"]

@app.get("/", response_class=HTMLResponse)
def index():
    messages_html = ""
    for sender, msg in chat_history:
        if sender == "You":
            messages_html += f'<div class="user-msg fade-in"><span>{msg}</span></div>'
        else:
            messages_html += f'<div class="bot-msg fade-in"><span>{msg}</span></div>'

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat Bot</title>
        <style>
            body {{
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: #fff;
                background-color: white;
            }}
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #121212;
                    background: radial-gradient(120% 120% at top right, #0d0d0d, #1a1a1a);
                }}
            }}

            .glass-container {{
                width: 95%;
                max-width: 550px;
                height: 80vh;
                background: rgba(255, 255, 255, 0.06);
                backdrop-filter: blur(40px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 28px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
            }}

            .chat-header {{
                padding: 1.5em;
                text-align: center;
                font-weight: 600;
                font-size: 1.8rem;
            }}

            .chat-box {{
                flex: 1;
                padding: 1.2em;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .bot-msg, .user-msg {{
                max-width: 80%;
                padding: 0.9em 1.1em;
                border-radius: 16px;
                font-size: 0.95rem;
                line-height: 1.5;
                animation: fadeIn 0.4s ease;
            }}

            .bot-msg {{
                align-self: flex-start;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}

            .user-msg {{
                align-self: flex-end;
                background: linear-gradient(145deg, #007aff, #005de0);
                box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
            }}

            .input-area {{
                display: flex;
                align-items: center;
                padding: 0.9em;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(255, 255, 255, 0.03);
            }}

            .input-area input {{
                flex: 1;
                padding: 0.8em 1em;
                border-radius: 12px;
                border: none;
                background: rgba(255, 255, 255, 0.1);
                color: #fff;
                font-size: 0.95rem;
                outline: none;
                transition: background 0.2s ease, box-shadow 0.2s ease;
            }}

            .input-area input:focus {{
                background: rgba(255, 255, 255, 0.15);
                box-shadow: 0 0 10px rgba(0, 122, 255, 0.3);
            }}

            .input-area button {{
                margin-left: 0.6em;
                background: linear-gradient(145deg, #007aff, #005de0);
                border: none;
                color: white;
                font-size: 1.2rem;
                padding: 0.6em 1em;
                border-radius: 12px;
                cursor: pointer;
                transition: 0.25s;
            }}

            .input-area button:hover {{
                background: linear-gradient(145deg, #338fff, #007aff);
                transform: scale(1.05);
            }}

            .fade-in {{
                animation: fadeIn 0.4s ease;
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(5px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="glass-container">
            <div class="chat-header">Chatbot</div>
            <div class="chat-box" id="chat-box">
                {messages_html if messages_html else '<div class="bot-msg fade-in">👋 Hey! I’m Gemini. Ask me anything.</div>'}
            </div>
            <form class="input-area" action="/" method="post" id="chat-form">
                <input name="message" id="message" placeholder="Type your message..." autocomplete="off" required />
                <button type="submit" title="Send">➤</button>
            </form>
        </div>
        <script>
            const chatBox = document.getElementById('chat-box');
            chatBox.scrollTop = chatBox.scrollHeight;
            document.getElementById('chat-form').addEventListener('submit', () => {{
                setTimeout(() => {{ chatBox.scrollTop = chatBox.scrollHeight; }}, 50);
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/", response_class=HTMLResponse)
def chat(message: str = Form(...)):
    message_clean = message.strip().lower()
    if message_clean in CLEAR_COMMANDS:
        chat_history.clear()
        chat_history.append(("Gemini", "🧹 All cleared! Ready for a fresh chat."))
        return index()

    chat_history.append(("You", message))
    response = bot.chat(message)
    chat_history.append(("Gemini", response))
    return index()