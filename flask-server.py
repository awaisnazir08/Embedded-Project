from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
from flask_cors import CORS
import os
import random

app = Flask(__name__)
CORS(app)

messages = []
CUSTOM_REPLIES = {
    'greeting': [
        "Message received and decrypted successfully!",
        "Got your secret message!",
        "Successfully processed your encrypted communication.",
        "Your message has been securely received and decoded."
    ],
    'error': [
        "Unable to process the message at this time.",
        "Error encountered during message processing.",
        "Message processing failed, please try again.",
        "System couldn't handle the request properly."
    ]
}

def caesar_decrypt(text, shift=-3):
    result = ""
    for char in text:
        if char.isalpha():
            is_upper = char.isupper()
            char_code = ord(char.lower()) - ord('a')
            new_code = (char_code - shift) % 26
            new_char = chr(new_code + ord('a'))
            result += new_char.upper() if is_upper else new_char
        else:
            result += char
    return result

def get_custom_reply(message_type='greeting'):
    replies = CUSTOM_REPLIES.get(message_type, CUSTOM_REPLIES['greeting'])
    return random.choice(replies)

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
        .encrypted, .decrypted {
            margin: 5px 0;
            word-wrap: break-word;
        }
        .label {
            font-weight: bold;
            color: #1a73e8;
        }
        .timestamp {
            color: #666;
            font-size: 0.8em;
        }
        .input-form {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .input-field {
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .submit-button {
            background-color: #1a73e8;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .submit-button:hover {
            background-color: #1557b0;
        }
        .response {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
    <script>
        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const responseDiv = document.getElementById('response');
            const message = messageInput.value.trim();
            
            if (!message) {
                showResponse('Please enter a message', false);
                return;
            }
            
            try {
                const response = await fetch('/send_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        encrypted_message: message
                    })
                });
                
                const data = await response.json();
                showResponse(data.message, response.ok);
                
                if (response.ok) {
                    messageInput.value = '';
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                }
            } catch (error) {
                showResponse('Error sending message: ' + error, false);
            }
        }
        
        function showResponse(message, isSuccess) {
            const responseDiv = document.getElementById('response');
            responseDiv.textContent = message;
            responseDiv.className = 'response ' + (isSuccess ? 'success' : 'error');
            responseDiv.style.display = 'block';
            
            setTimeout(() => {
                responseDiv.style.display = 'none';
            }, 3000);
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Encrypted Messages</h1>
        
        <div class="input-form">
            <h2>Send Message</h2>
            <input type="text" id="messageInput" class="input-field" 
                   placeholder="Enter your encrypted message here..." 
                   onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()" class="submit-button">Send Message</button>
            <div id="response" class="response"></div>
        </div>
        
        <div class="messages-container">
            {% for message in messages %}
            <div class="message">
                <div class="encrypted">
                    <span class="label">Encrypted:</span> {{ message['encrypted_text'] }}
                </div>
                <div class="decrypted">
                    <span class="label">Decrypted:</span> {{ message['decrypted_text'] }}
                </div>
                <div class="timestamp">Received: {{ message['timestamp'] }}</div>
            </div>
            {% endfor %}
        </div>
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
            decrypted_message = caesar_decrypt(encrypted_message)
            custom_reply = get_custom_reply()
            
            messages.append({
                'encrypted_text': encrypted_message,
                'decrypted_text': decrypted_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            while len(messages) > 10:
                messages.pop(0)
                
            return jsonify({
                'status': 'success',
                'message': custom_reply,
                'decrypted_text': decrypted_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }), 200
        else:
            error_reply = get_custom_reply('error')
            return jsonify({
                'status': 'error',
                'message': error_reply
            }), 400
            
    except Exception as e:
        error_reply = get_custom_reply('error')
        return jsonify({
            'status': 'error',
            'message': f"{error_reply} Details: {str(e)}"
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host='0.0.0.0', port=port)