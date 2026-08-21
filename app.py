from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, subprocess, qrcode
from io import BytesIO

app = Flask(__name__)
DB_PATH = '/opt/render/project/src/database.db' if os.environ.get('RENDER') else 'database.db'
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
    conn.execute('CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, attendance TEXT, meal TEXT, song TEXT, notes TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS guestbook (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    data = request.json
    name, att = data.get('guest_name'), data.get('attendance')
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO guests (name, attendance, meal, song, notes) VALUES (?, ?, ?, ?, ?)", (name, att, data.get('meal'), data.get('song'), data.get('notes')))
    conn.commit()
    conn.close()
    trigger_phone_ping(f"RSVP: {name} is {att}!")
    return jsonify({"success": True})

@app.route('/api/comment', methods=['POST'])
def add_comment():
    data = request.json
    name, msg = data.get('name'), data.get('message')
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO guestbook (name, message) VALUES (?, ?)", (name, msg))
    conn.commit()
    conn.close()
    trigger_phone_ping(f"Note from {name}")
    return jsonify({"success": True})

@app.route('/api/comments')
def get_comments():
    conn = sqlite3.connect(DB_PATH)
    comments = conn.execute("SELECT name, message, timestamp FROM guestbook ORDER BY timestamp DESC").fetchall()
    conn.close()
    return jsonify([{"name": c[0], "message": c[1], "time": c[2]} for c in comments])

@app.route('/qr')
def get_qr():
    img = qrcode.make("http://192.168.100.132:5000")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/master-view/<pin>')
def admin(pin):
    if pin != '1234': return 'UNAUTHORIZED', 401
    conn = sqlite3.connect(DB_PATH)
    guests = conn.execute("SELECT * FROM guests").fetchall()
    stats = conn.execute("SELECT attendance, COUNT(*) FROM guests GROUP BY attendance").fetchall()
    comments = conn.execute("SELECT name, message FROM guestbook ORDER BY timestamp DESC").fetchall()
    conn.close()
    stat_html = "<h3>Stats</h3><ul>"
    for s in stats: stat_html += f"<li>{s[0].upper()}: {s[1]}</li>"
    stat_html += "</ul>"
    html = f"<html><body><h1>Master Control</h1>{stat_html}<table border='1'><tr><th>Name</th><th>Status</th></tr>"
    for g in guests: html += f"<tr><td>{g[1]}</td><td>{g[2]}</td></tr>"
    html += "</table><h2>Messages</h2><ul>"
    for c in comments: html += f"<li><b>{c[0]}:</b> {c[1]}</li>"
    return html + "</ul></body></html>"

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000, host='0.0.0.0')
