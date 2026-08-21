from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, subprocess, csv, io

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
    conn.commit()
    conn.close()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    data = request.json
    name, att, meal, song, notes = data.get('guest_name'), data.get('attendance'), data.get('meal'), data.get('song'), data.get('notes')
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO guests (name, attendance, meal, song, notes) VALUES (?, ?, ?, ?, ?)", (name, att, meal, song, notes))
    conn.commit()
    conn.close()
    trigger_phone_ping(f"RSVP: {name}")
    return jsonify({"success": True})

@app.route('/api/songs')
def get_songs():
    conn = sqlite3.connect(DB_PATH)
    songs = conn.execute("SELECT name, song FROM guests WHERE song != '' ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"name": s[0], "song": s[1]} for s in songs])

@app.route('/master-view/<pin>')
def admin(pin):
    if pin != '1234': return 'UNAUTHORIZED', 401
    conn = sqlite3.connect(DB_PATH)
    guests = conn.execute("SELECT * FROM guests").fetchall()
    conn.close()
    html = f"<html><body style='font-family:sans-serif;padding:20px;'><h1>Admin Hub</h1><a href='/export-csv/1234'>DOWNLOAD CSV</a><br><br><table border='1'><tr><th>Name</th><th>Status</th><th>Meal</th><th>Song</th></tr>"
    for g in guests: html += f"<tr><td>{g[1]}</td><td>{g[2]}</td><td>{g[3]}</td><td>{g[4]}</td></tr>"
    return html + "</table><br><a href='/'>Back</a></body></html>"

@app.route('/export-csv/<pin>')
def export_csv(pin):
    if pin != '1234': return 'UNAUTHORIZED', 401
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM guests")
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow([d[0] for d in cursor.description])
    cw.writerows(cursor.fetchall())
    output = io.BytesIO(si.getvalue().encode('utf-8'))
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='rsvps.csv')

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000, host='0.0.0.0')
