from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, subprocess, qrcode
from io import BytesIO

app = Flask(__name__)
DB_PATH = 'database.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def trigger_phone_ping(msg):
    adb = r'C:\Users\Admin\AppData\Local\Android\Sdk\platform-tools\adb.exe'
    dev = 'adb-R5CY33H4PAF-9vXPPX._adb-tls-connect._tcp'
    try:
        subprocess.run([adb, '-s', dev, 'shell', 'cmd', 'vibrator', 'vibrate', '500'], capture_output=True)
        subprocess.run([adb, '-s', dev, 'shell', 'am', 'broadcast', '-a', 'com.example.kineticvault.NUDGE', '--es', 'msg', msg], capture_output=True)
    except: pass

def init_db():
    if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, attendance TEXT, meal TEXT, song TEXT, notes TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS guestbook (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    data = request.json
    name = data.get('guest_name', 'Unknown')
    att = data.get('attendance', 'no')
    meal = data.get('meal', '')
    song = data.get('song', '')
    notes = data.get('notes', '')
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO guests (name, attendance, meal, song, notes) VALUES (?, ?, ?, ?, ?)", (name, att, meal, song, notes))
        conn.commit()
        conn.close()
        trigger_phone_ping(f"RSVP: {name}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/comment', methods=['POST'])
def add_comment():
    data = request.json
    name = data.get('name', 'Anonymous')
    msg = data.get('message', '')
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO guestbook (name, message) VALUES (?, ?)", (name, msg))
        conn.commit()
        conn.close()
        trigger_phone_ping(f"Note from {name}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/comments')
def get_comments():
    conn = sqlite3.connect(DB_PATH)
    comments = conn.execute("SELECT name, message, timestamp FROM guestbook ORDER BY timestamp DESC").fetchall()
    conn.close()
    return jsonify([{"name": c[0], "message": c[1], "time": c[2]} for c in comments])

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"success": False}), 400
    file = request.files['file']
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO memories (filename, caption) VALUES (?, ?)", (file.filename, request.form.get('caption', '')))
    conn.commit()
    conn.close()
    trigger_phone_ping("New Photo!")
    return jsonify({"success": True})

@app.route('/api/memories')
def get_memories():
    conn = sqlite3.connect(DB_PATH)
    mems = conn.execute("SELECT filename FROM memories").fetchall()
    conn.close()
    return jsonify([{"url": f"/static/uploads/{m[0]}"} for m in mems])

@app.route('/master-view/<pin>')
def admin(pin):
    if pin != '1234': return 'UNAUTHORIZED', 401
    conn = sqlite3.connect(DB_PATH)
    guests = conn.execute("SELECT * FROM guests").fetchall()
    conn.close()
    html = "<h1>Master Guest List</h1><table border='1'><tr><th>Name</th><th>Attending</th><th>Meal</th><th>Song</th></tr>"
    for g in guests: html += f"<tr><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td>{g[4]}</td></tr>"
    return html + "</table><br><a href='/'>Back</a>"

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000, host='0.0.0.0')

