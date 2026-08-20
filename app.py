from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

# Cloud Path Adjustment
DB_PATH = '/opt/render/project/src/database.db' if os.environ.get('RENDER') else 'database.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, attendance TEXT, meal TEXT, notes TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)')
    conn.commit()
    conn.close()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    conn.execute(\"INSERT INTO guests (name, attendance, meal, notes) VALUES (?, ?, ?, ?)\", (data.get('guest_name'), data.get('attendance'), data.get('meal'), data.get('notes')))
    conn.commit()
    conn.close()
    return jsonify({\"success\": True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(\"INSERT INTO memories (filename, caption) VALUES (?, ?)\", (file.filename, request.form.get('caption', '')))
    conn.commit()
    conn.close()
    return jsonify({\"success\": True})

@app.route('/api/memories')
def get_memories():
    conn = sqlite3.connect(DB_PATH)
    mems = conn.execute(\"SELECT * FROM memories\").fetchall()
    conn.close()
    return jsonify([{\"url\": f\"/static/uploads/{m[1]}\"} for m in mems])

@app.route('/master-view')
def admin():
    conn = sqlite3.connect(DB_PATH)
    guests = conn.execute(\"SELECT * FROM guests\").fetchall()
    conn.close()
    html = \"<h1>Master Guest List</h1><table border='1'>\"
    for g in guests: html += f\"<tr><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td>{g[4]}</td></tr>\"
    return html + \"</table>\"

if __name__ == '__main__':
    init_db()
    # app.run managed by Gunicorn
