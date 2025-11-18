from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import re

app = Flask(__name__)

# Initialize Gemini API
# Replace 'YOUR_API_KEY' with your actual Gemini API key
genai.configure(api_key='AIzaSyB37-_m8iichYejeidCaziWsIAUOgApHd8')
model = genai.GenerativeModel('gemini-2.0-flash')

def format_response(response):
    # Add markdown formatting instructions to the model
    formatted_response = response.text
    
    # Ensure code blocks are properly formatted
    formatted_response = re.sub(
        r'```(\w+)?\n(.*?)\n```',
        r'```\1\n\2\n```',
        formatted_response,
        flags=re.DOTALL
    )
    
    return formatted_response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']
        
        # Add formatting instructions to the prompt
        prompt = f"""Please provide a response to: {user_message}

        Format your response using the following guidelines:
        - Use **bold** for emphasis
        - Use *italics* for technical terms
        - Use proper markdown code blocks with language specification
        - Use bullet points where appropriate
        - Include line breaks for readability
        - Format code examples in ```language\ncode\n``` blocks
        """
        
        response = model.generate_content(prompt)
        formatted_response = format_response(response)
        
        return jsonify({'response': formatted_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
