from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Store messages in memory (could be replaced with a database)
messages = []

# Shared variable to hold the custom response option
response_option = "Default response: Your message has been successfully processed."


def caesar_decrypt(encrypted_text, shift=3):
    """
    Decrypt text using Caesar cipher with specified shift.
    Handles both letters (a-z, A-Z) and numbers (0-9).
    
    Args:
        encrypted_text (str): Text to decrypt
        shift (int): Number of positions to shift back (default 3)
    
    Returns:
        str: Decrypted text
    """
    decrypted_text = ""
    for char in encrypted_text:
        if char.isalpha():
            # Handle letters (a-z, A-Z)
            ascii_base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - ascii_base - shift) % 26
            decrypted_text += chr(shifted + ascii_base)
        elif char.isdigit():
            # Handle numbers (0-9)
            # Convert to 0-9 range, apply shift, wrap around 10 positions
            num = int(char)
            shifted = (num - shift) % 10
            decrypted_text += str(shifted)
        else:
            # Keep other characters unchanged
            decrypted_text += char
    return decrypted_text


# Updated HTML template with decrypted messages
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
        }
        .label {
            font-weight: bold;
            color: #1a73e8;
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
</body>
</html>
'''


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, messages=messages)


@app.route('/set_response', methods=['GET', 'POST'])
def set_response():
    global response_option
    if request.method == 'POST':
        # Update the response option dynamically
        response_option = request.form.get('new_response', response_option)
        return render_template_string('''
            <p>Response option updated successfully!</p>
            <a href="/set_response">Go back</a>
        ''')
    
    # Render a form to update the response option
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Set Custom Response Option</title>
        </head>
        <body>
            <h1>Set Custom Response Option</h1>
            <form method="POST">
                <label for="new_response">Enter new response option:</label>
                <input type="text" id="new_response" name="new_response" placeholder="Type your custom response here">
                <button type="submit">Update Response</button>
            </form>
        </body>
        </html>
    ''')


@app.route('/send_data', methods=['POST'])
def receive_data():
    global response_option
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        
        if encrypted_message:
            # Decrypt the message
            decrypted_message = caesar_decrypt(encrypted_message)
            
            messages.append({
                'encrypted_text': encrypted_message,
                'decrypted_text': decrypted_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Keep only last 10 messages
            while len(messages) > 10:
                messages.pop(0)
                
            return jsonify({
                'status': 'success',
                'message': 'Data received',
                'decrypted_text': decrypted_message,
                'response_option': response_option  # Use the updated response option
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'No message provided',
                'response_option': response_option  # Use the updated response option
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'response_option': response_option  # Use the updated response option
        }), 400


if __name__ == '__main__':
    # Use environment variables for production settings
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
