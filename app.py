#!/usr/bin/env python3
"""
Fabric Data Agent Flask Chat Interface (Fixed Authentication)
"""

import os
from flask import Flask, render_template_string, request, session, redirect, url_for
from fabric_data_agent_client import FabricDataAgentClient

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Configuration ---
TENANT_ID = os.getenv("TENANT_ID", "your-tenant-id-here")
DATA_AGENT_URL = os.getenv("DATA_AGENT_URL", "your-data-agent-url-here")

# --- Authenticate once at startup ---
client = None

def init_fabric_client():
    global client
    try:
        print("🔐 Initialising Fabric Data Agent Client...")
        client = FabricDataAgentClient(
            tenant_id=TENANT_ID,
            data_agent_url=DATA_AGENT_URL
        )
        print("✅ Authentication successful!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        client = None

# --- HTML Template ---
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fabric Data Agent Chat</title>
<style>
/* Styling omitted for brevity — same as your version */
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
                chat.append({"role": "agent", "text": "⚠️ Data Agent client not initialised. Please restart the app."})
                session["chat"] = chat
                return render_template_string(HTML, chat=chat)

            try:
                response = client.ask(question)
                chat.append({"role": "agent", "text": response})
            except Exception as e:
                chat.append({"role": "agent", "text": f"❌ Error: {e}"})

            session["chat"] = chat

    return render_template_string(HTML, chat=chat)


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.pop("chat", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("🚀 Starting Fabric Data Agent Flask Chat Interface...")
    init_fabric_client()  # Authenticate once at startup
    app.run(host="0.0.0.0", port=8080, debug=True)
