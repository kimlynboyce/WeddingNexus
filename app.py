from flask import Flask, render_template, request, jsonify, send_file, session
import sqlite3, os, subprocess, qrcode
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'wedding_secret_key'
DB_PATH = 'database.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    d = request.json
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO guests (name, attendance, meal, song, notes) VALUES (?, ?, ?, ?, ?)", (d.get('guest_name'), d.get('attendance'), d.get('meal'), d.get('song'), d.get('notes')))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/toast', methods=['POST'])
def add_toast():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE stats SET toasts = toasts + 1 WHERE id = 1')
    res = conn.execute('SELECT toasts FROM stats WHERE id = 1').fetchone()
    conn.commit()
    conn.close()
    return jsonify({"toasts": res[0]})

@app.route('/api/toasts')
def get_toasts():
    conn = sqlite3.connect(DB_PATH)
    res = conn.execute('SELECT toasts FROM stats WHERE id = 1').fetchone()
    conn.close()
    return jsonify({"toasts": res[0] if res else 0})

@app.route('/qr')
def get_qr():
    img = qrcode.make("https://weddingnexus.onrender.com")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('pin') == '1234':
            session['admin'] = True
            return jsonify({"success": True})
        return jsonify({"success": False}), 401
    return render_template('login.html')

@app.route('/master-hub')
def admin_hub():
    if not session.get('admin'): return "UNAUTHORIZED", 401
    conn = sqlite3.connect(DB_PATH)
    guests = conn.execute("SELECT * FROM guests").fetchall()
    conn.close()
    return f"<h1>Guests</h1><p>{str(guests)}</p>"

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000)
