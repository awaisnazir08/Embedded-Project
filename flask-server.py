from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
from flask_cors import CORS  # Import CORS
import os

app = Flask(__name__)
CORS(app)

# Store messages in memory (could be replaced with a database)
messages = []

# HTML template with some basic styling
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Encrypted Messages</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a73e8;
            text-align: center;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border-left: 4px solid #1a73e8;
            border-radius: 4px;
        }
        .timestamp {
            color: #666;
            font-size: 0.8em;
        }
        .refresh-button {
            background-color: #1a73e8;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-button:hover {
            background-color: #1557b0;
        }
    </style>
    <script>
        function refreshPage() {
            location.reload();
        }
        
        // Auto-refresh every 10 seconds
        setInterval(refreshPage, 10000);
    </script>
</head>
<body>
    <div class="container">
        <h1>Encrypted Messages</h1>
        <button class="refresh-button" onclick="refreshPage()">Refresh Messages</button>
        {% for message in messages %}
        <div class="message">
            <div>{{ message['text'] }}</div>
            <div class="timestamp">Received: {{ message['timestamp'] }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, messages=messages)

@app.route('/send_data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        
        if encrypted_message:
            messages.append({
                'text': encrypted_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Keep only last 10 messages
            while len(messages) > 10:
                messages.pop(0)
                
            return jsonify({'status': 'success', 'message': 'Data received'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No message provided'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    # Use environment variables for production settings
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
