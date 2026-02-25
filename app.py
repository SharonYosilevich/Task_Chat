# Implemented by Sharon Yosilevich (Person A)
from flask import Flask, send_file, request
import os
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

# Database configuration: set MYSQL_URI environment variable to a MySQL
# SQLAlchemy URI like: mysql+pymysql://user:pass@host:3306/dbname
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('MYSQL_URI') or os.environ.get('DATABASE_URL') or 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(100), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

# 1. Serve the static HTML for any room
@app.route('/', defaults={'room': 'general'})
@app.route('/<room>')
def serve_frontend(room):
    # Always return the static index.html, regardless of room
    return send_file('templates/index.html')

# 3. GET /api/chat/<room> - Return chat history for a room
@app.route('/api/chat/<room>', methods=['GET', 'POST'])
def get_chat(room):
    # POST -> insert into DB
    if request.method == 'POST':
        username = request.form.get('username') or (request.json and request.json.get('username')) or 'Anonymous'
        msg = request.form.get('msg') or (request.json and request.json.get('msg')) or ''
        username = str(username).strip()
        msg = str(msg).strip()
        timestamp = datetime.now()
        m = Message(room=room, timestamp=timestamp, username=username, text=msg)
        db.session.add(m)
        db.session.commit()
        return ('', 204)

    # GET -> return concatenated formatted messages for room
    msgs = Message.query.filter_by(room=room).order_by(Message.timestamp).all()
    if not msgs:
        return ""
    lines = []
    for m in msgs:
        ts = m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f'[{ts}] {m.username}: {m.text}')
    return "\n".join(lines)

if __name__ == '__main__':
    app.run(debug=True)
