from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not GEMINI_API_KEY:
            return jsonify({
                'error': 'API key not configured. Please set GEMINI_API_KEY environment variable.'
            }), 400
        
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get chat history from session
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        chat_history = session['chat_history']
        
        # Start a chat session with history
        chat = model.start_chat(history=[
            {'role': msg['role'], 'parts': [msg['content']]}
            for msg in chat_history
        ])
        
        # Send message and get response
        response = chat.send_message(user_message)
        bot_response = response.text
        
        # Update chat history
        chat_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        chat_history.append({
            'role': 'model',
            'content': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages to avoid session overflow
        session['chat_history'] = chat_history[-20:]
        session.modified = True
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    session['chat_history'] = []
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
