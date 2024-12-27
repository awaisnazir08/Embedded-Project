from flask import Flask, request, render_template_string, jsonify, redirect, url_for
from datetime import datetime
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

# Store messages in memory (could be replaced with a database)
messages = []

# Shared variable to hold the custom response option
response_option = "Default response: Your message has been successfully processed."

# Temporary store for pending responses
pending_requests = {}

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
            ascii_base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - ascii_base - shift) % 26
            decrypted_text += chr(shifted + ascii_base)
        elif char.isdigit():
            num = int(char)
            shifted = (num - shift) % 10
            decrypted_text += str(shifted)
        else:
            decrypted_text += char
    return decrypted_text


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, messages=messages)


@app.route('/set_response', methods=['GET', 'POST'])
def set_response():
    global response_option
    if request.method == 'POST':
        # Update the response option dynamically
        response_option = request.form.get('new_response', response_option)
        pending_id = request.form.get('pending_id')
        
        if pending_id and pending_id in pending_requests:
            pending_request = pending_requests.pop(pending_id)
            encrypted_message = pending_request['encrypted_message']
            decrypted_message = pending_request['decrypted_message']
            
            # Store the processed message
            messages.append({
                'encrypted_text': encrypted_message,
                'decrypted_text': decrypted_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Respond to the original client
            return pending_request['callback']({
                'status': 'success',
                'message': 'Data received',
                'decrypted_text': decrypted_message,
                'response_option': response_option
            })
        
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
                <input type="hidden" name="pending_id" value="{{ pending_id }}">
                <label for="new_response">Enter new response option:</label>
                <input type="text" id="new_response" name="new_response" placeholder="Type your custom response here">
                <button type="submit">Update Response</button>
            </form>
        </body>
        </html>
    ''', pending_id=request.args.get('pending_id'))


@app.route('/send_data', methods=['POST'])
def receive_data():
    global response_option
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        
        if encrypted_message:
            # Decrypt the message
            decrypted_message = caesar_decrypt(encrypted_message)
            
            # Generate a unique ID for this request
            pending_id = str(uuid.uuid4())
            
            # Save the pending request
            pending_requests[pending_id] = {
                'encrypted_message': encrypted_message,
                'decrypted_message': decrypted_message,
                'callback': lambda response: jsonify(response)
            }
            
            # Redirect to set response page with the pending ID
            return redirect(url_for('set_response', pending_id=pending_id))
        
        else:
            return jsonify({
                'status': 'error',
                'message': 'No message provided',
                'response_option': response_option
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'response_option': response_option
        }), 400


if __name__ == '__main__':
    # Use environment variables for production settings
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
