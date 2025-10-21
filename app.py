#!/usr/bin/env python3
"""
Fabric Data Agent Flask Chat Interface
"""

import os
import logging
from flask import Flask, render_template_string, request, session, redirect, url_for
from fabric_data_agent_client import FabricDataAgentClient

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

app = Flask(_name_)
app.secret_key = "supersecretkey"

# --- Configuration ---
TENANT_ID = os.getenv("TENANT_ID", "your-tenant-id-here")
DATA_AGENT_URL = os.getenv("DATA_AGENT_URL", "your-data-agent-url-here")

# --- Global client instance ---
client = None

def init_fabric_client():
    global client
    try:
        logger.info("🔐 Initializing Fabric Data Agent Client...")
        client = FabricDataAgentClient(
            tenant_id=TENANT_ID,
            data_agent_url=DATA_AGENT_URL
        )
        logger.info("✅ Authentication successful!")
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        client = None

# --- HTML Template ---
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fabric Data Agent Chat</title>
<style>
/* Styling omitted for brevity */
body { font-family: Arial; background: #f3f3f3; }
header { display: flex; align-items: center; padding: 10px; background: #222; color: white; }
.chat-container { max-width: 600px; margin: auto; background: white; border-radius: 5px; padding: 20px; margin-top: 20px; }
.chat-box { max-height: 400px; overflow-y: auto; }
.message { margin-bottom: 10px; }
.message.user .bubble { background: #007bff; color: white; }
.message.agent .bubble { background: #e5e5ea; }
.bubble { padding: 10px 15px; border-radius: 15px; display: inline-block; }
.input-bar { display: flex; margin-top: 10px; }
textarea { flex: 1; resize: none; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
.send-btn { background: #007bff; border: none; color: white; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
</style>
</head>
<body>
    <header>
        <h1>🧩 Fabric Data Agent</h1>
        <div style="margin-left:auto;">
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
            <textarea name="question" placeholder="Type your question here..." required></textarea>
            <button type="submit" class="send-btn">Send</button>
        </form>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        chatBox.scrollTop = chatBox.scrollHeight;
    </script>
</body>
</html>"""

@app.route("/", methods=["GET", "POST"])
def index():
    if TENANT_ID == "your-tenant-id-here" or DATA_AGENT_URL == "your-data-agent-url-here":
        return "<h3>❌ Please set TENANT_ID and DATA_AGENT_URL first.</h3>"

    if "chat" not in session:
        session["chat"] = []
    chat = session["chat"]

    if request.method == "POST":
        question = request.form.get("question")
        if question:
            chat.append({"role": "user", "text": question})
            session["chat"] = chat

            if client is None:
                logger.warning("⚠ Client is None when trying to handle question.")
                chat.append({"role": "agent", "text": "⚠ Data Agent client not initialized. Please restart the app."})
                session["chat"] = chat
                return render_template_string(HTML, chat=chat)

            try:
                logger.info("📡 Sending question to Fabric Data Agent...")
                response = client.ask(question)
                chat.append({"role": "agent", "text": response})
            except Exception as e:
                logger.error(f"❌ Error while querying the agent: {e}")
                chat.append({"role": "agent", "text": f"❌ Error: {e}"})

            session["chat"] = chat

    return render_template_string(HTML, chat=chat)

@app.route("/clear", methods=["POST"])
def clear_chat():
    session.pop("chat", None)
    return redirect(url_for("index"))

if _name_ == "_main_":
    logger.info("🚀 Starting Fabric Data Agent Flask Chat Interface...")
    init_fabric_client()
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)
