# Implemented by Sharon Yosilevich (Person A)
from flask import Flask, send_file, request
import os
from datetime import datetime

app = Flask(__name__)

# 1. Serve the static HTML for any room
@app.route('/', defaults={'room': 'general'})
@app.route('/<room>')
def serve_frontend(room):
    # Always return the static index.html, regardless of room
    return send_file('index.html')

# 3. GET /api/chat/<room> - Return chat history for a room
@app.route('/api/chat/<room>', methods=['GET', 'POST'])
def get_chat(room):
    messages_file = f"chat_{room}.txt"
    if request.method == 'POST':
        # Accept form or JSON payload
        username = request.form.get('username') or (request.json and request.json.get('username')) or 'Anonymous'
        msg = request.form.get('msg') or (request.json and request.json.get('msg')) or ''
        username = str(username).strip()
        msg = str(msg).strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {username}: {msg}\n"
        os.makedirs(os.path.dirname(messages_file) or '.', exist_ok=True)
        with open(messages_file, 'a', encoding='utf-8') as f:
            f.write(line)
    if not os.path.exists(messages_file):
        return ""
    with open(messages_file, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True)
