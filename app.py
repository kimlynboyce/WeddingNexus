from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, subprocess, csv, io, qrcode
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
    conn.execute('CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, attendance TEXT, meal TEXT, song TEXT, notes TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS guestbook (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, toasts INTEGER DEFAULT 0)')
    if not conn.execute('SELECT * FROM stats').fetchone(): conn.execute('INSERT INTO stats (id, toasts) VALUES (1, 0)')
    conn.commit()
    conn.close()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO guests (name, attendance, meal, song, notes) VALUES (?, ?, ?, ?, ?)", (data.get('guest_name'), data.get('attendance'), data.get('meal'), data.get('song'), data.get('notes')))
    conn.commit()
    conn.close()
    trigger_phone_ping(f"RSVP: {data.get('guest_name')}")
    return jsonify({"success": True})

@app.route('/api/toast', methods=['POST'])
def add_toast():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE stats SET toasts = toasts + 1 WHERE id = 1')
    res = conn.execute('SELECT toasts FROM stats WHERE id = 1').fetchone()
    conn.commit()
    conn.close()
    trigger_phone_ping(f"VIRTUAL TOAST! Total: {res[0]}")
    return jsonify({"toasts": res[0]})

@app.route('/api/toasts')
def get_toasts():
    conn = sqlite3.connect(DB_PATH)
    res = conn.execute('SELECT toasts FROM stats WHERE id = 1').fetchone()
    conn.close()
    return jsonify({"toasts": res[0]})

@app.route('/master-view/<pin>')
def admin(pin):
    if pin != '1234': return 'UNAUTHORIZED', 401
    conn = sqlite3.connect(DB_PATH)
    guests = conn.execute("SELECT * FROM guests").fetchall()
    toasts = conn.execute('SELECT toasts FROM stats WHERE id = 1').fetchone()[0]
    conn.close()
    html = f"<html><body style='font-family:sans-serif;padding:30px;background:#f8f9fa;'><h1>Wedding Dashboard</h1><h3>Total Toasts: {toasts}</h3><a href='/export-csv/1234' style='padding:10px 20px;background:#046307;color:white;text-decoration:none;border-radius:5px;'>DOWNLOAD CSV</a><br><br><table border='1' style='width:100%;border-collapse:collapse;'> <tr style='background:#046307;color:white;'><th>Name</th><th>Status</th><th>Meal</th><th>Song</th></tr>"
    for g in guests: html += f"<tr><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td>{g[4]}</td></tr>"
    return html + "</table></body></html>"

@app.route('/qr')
def get_qr():
    img = qrcode.make("http://192.168.100.132:5000")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000, host='0.0.0.0')
