#!/usr/bin/env python3
"""
Fabric Data Agent Flask Chat Interface
--------------------------------------
This Flask app provides a simple chat-style web interface
to interact with your Microsoft Fabric Data Agent.

Make sure you have installed dependencies:
    pip install flask fabric-data-agent-client
"""

import os
from flask import Flask, render_template_string, request, session, redirect, url_for
from fabric_data_agent_client import FabricDataAgentClient

# Flask setup
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration: from environment or edit directly
TENANT_ID = os.getenv("TENANT_ID", "your-tenant-id-here")
DATA_AGENT_URL = os.getenv("DATA_AGENT_URL", "your-data-agent-url-here")

# HTML template for the chat interface
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fabric Data Agent Chat</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background-color: #f5f7fa;
            display: flex; flex-direction: column;
            height: 100vh;
        }
        header {
            display: flex; align-items: center; justify-content: space-between;
            background: linear-gradient(90deg, #0078d4, #005fa3);
            color: white; padding: 12px 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        header .logo { font-size: 1.6rem; }
        header h1 { margin: 0; font-size: 1.2rem; flex: 1; text-align: center; }
        header .clear-btn form { margin: 0; }
        header .clear-btn button {
            background-color: white; color: #0078d4;
            border: none; padding: 6px 14px;
            border-radius: 8px; cursor: pointer; font-weight: 600;
        }
        header .clear-btn button:hover { background-color: #e8f0fc; }

        .chat-container {
            flex: 1; display: flex; flex-direction: column;
            justify-content: space-between; max-width: 850px;
            margin: 0 auto; width: 100%;
            border-radius: 14px; background: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden; position: relative; margin-top: 20px;
        }
        .chat-box {
            flex: 1; padding: 24px; overflow-y: auto;
            background-color: #fafafa; scroll-behavior: smooth;
        }
        .message { margin-bottom: 18px; display: flex; animation: fadeIn 0.3s ease; }
        .user { justify-content: flex-end; }
        .agent { justify-content: flex-start; }
        .bubble {
            padding: 12px 16px; border-radius: 20px;
            max-width: 70%; font-size: 15px; line-height: 1.4;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .user .bubble {
            background-color: #0078d4; color: white; border-bottom-right-radius: 5px;
        }
        .agent .bubble {
            background-color: #e9ecef; color: #333; border-bottom-left-radius: 5px;
        }
        @keyframes fadeIn { from {opacity: 0; transform: translateY(5px);} to {opacity: 1; transform: translateY(0);} }

        .input-bar {
            display: flex; align-items: center; padding: 10px 16px;
            background: white; border-top: 1px solid #ddd; position: sticky; bottom: 0;
        }
        .input-wrapper { position: relative; flex: 1; }
        textarea {
            width: 100%; border: 1px solid #ccc; border-radius: 25px;
            padding: 12px 45px 12px 15px; font-size: 15px;
            resize: none; outline: none; background-color: #f8f9fb;
            transition: border 0.2s;
        }
        textarea:focus { border: 1px solid #0078d4; background-color: white; }
        .send-btn {
            position: absolute; right: 8px; top: 50%;
            transform: translateY(-50%); background-color: #0078d4;
            border: none; color: white; width: 36px; height: 36px;
            border-radius: 50%; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: background 0.3s ease;
        }
        .send-btn:hover { background-color: #005fa3; }
        .send-btn svg { width: 18px; height: 18px; transform: rotate(-45deg); }
    </style>
</head>
<body>
    <header>
        <div class="logo">🧩</div>
        <h1>Fabric Data Agent</h1>
        <div class="clear-btn">
            <form action="{{ url_for('clear_chat') }}" method="post">
                <button type="submit">Clear Chat</button>
            </form>
        </div>
    </header>

    <div class="chat-container">
        <div class="chat-box" id="chatBox">
            {% if chat %}
                {% for msg in chat %}
                    <div class="message {{ msg.role }}">
                        <div class="bubble">{{ msg.text|safe }}</div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="message agent">
                    <div class="bubble">👋 Hello! I’m your Fabric Data Agent. Ask me something to begin.</div>
                </div>
            {% endif %}
        </div>

        <form method="post" class="input-bar">
            <div class="input-wrapper">
                <textarea name="question" placeholder="Type your question here..." required></textarea>
                <button type="submit" class="send-btn" title="Send">
                    <svg viewBox="0 0 24 24" fill="none">
                        <path d="M5 12h14M12 5l7 7-7 7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
        </form>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        chatBox.scrollTop = chatBox.scrollHeight;
    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    # Check configuration
    if TENANT_ID == "your-tenant-id-here" or DATA_AGENT_URL == "your-data-agent-url-here":
        return (
            "<h3 style='font-family:Segoe UI;color:#d9534f;'>❌ Please configure TENANT_ID and DATA_AGENT_URL "
            "in environment variables or directly in app.py</h3>"
        )

    # Start chat session
    if "chat" not in session:
        session["chat"] = []
    chat = session["chat"]

    # Initialise Fabric Client (with browser auth)
    try:
        client = FabricDataAgentClient(
            tenant_id=TENANT_ID,
            data_agent_url=DATA_AGENT_URL
        )
    except Exception as e:
        return f"<h3>❌ Error initialising Fabric Data Agent Client: {e}</h3>"

    if request.method == "POST":
        question = request.form.get("question")
        if question:
            # Add user message
            chat.append({"role": "user", "text": question})
            session["chat"] = chat

            try:
                # Call Fabric Data Agent
                response = client.ask(question)

                # Add agent message
                chat.append({"role": "agent", "text": response})
                session["chat"] = chat
            except Exception as e:
                error_msg = f"⚠️ Error fetching response: {str(e)}"
                chat.append({"role": "agent", "text": error_msg})
                session["chat"] = chat

    return render_template_string(HTML, chat=chat)


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.pop("chat", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("🚀 Starting Fabric Data Agent Flask Chat Interface...")
    print("➡️  Visit http://localhost:8080 in your browser")
    app.run(host="0.0.0.0", port=8080, debug=True)
