from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use the correct model from Gemini 2.5 family
    model = genai.GenerativeModel("models/gemini-2.5-flash")
else:
    model = None

@app.route("/")
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not GEMINI_API_KEY:
            return jsonify({"error": "GEMINI_API_KEY not configured"}), 400

        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        chat_history = session.get("chat_history", [])

        chat = model.start_chat(history=[
            {"role": msg["role"], "parts": [msg["content"]]}
            for msg in chat_history
        ])

        response = chat.send_message([user_message])
        bot_response = response.text

        chat_history.append({"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()})
        chat_history.append({"role": "model", "content": bot_response, "timestamp": datetime.now().isoformat()})

        session["chat_history"] = chat_history[-20:]
        session.modified = True

        return jsonify({"response": bot_response, "timestamp": datetime.now().isoformat()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear_history():
    session["chat_history"] = []
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

