from flask import Flask, render_template, request, jsonify, send_file, session
import os, qrcode, smtplib
from io import BytesIO
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
import psycopg2

app = Flask(__name__)
app.secret_key = 'wedding_secret_key'

DATABASE_URL = os.environ.get('DATABASE_URL')
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS guests (id SERIAL PRIMARY KEY, name TEXT, attendance TEXT, meal TEXT, song TEXT, notes TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS memories (id SERIAL PRIMARY KEY, filename TEXT, caption TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, toasts INTEGER DEFAULT 0)')
    cur.execute('SELECT * FROM stats WHERE id = 1')
    if not cur.fetchone():
        cur.execute('INSERT INTO stats (id, toasts) VALUES (1, 28)')
    conn.commit()
    cur.close()
    conn.close()

init_db()

def send_rsvp_email(data):
    sender = "kimlynboyce5@gmail.com"
    password = "hhdnkcnqngbqqhjo"
    recipient = "kimlynboyce5@gmail.com"
    try:
        body = (
            f"New RSVP received!\n\n"
            f"Name: {data.get('guest_name')}\n"
            f"Attending: {'Yes' if data.get('attendance') == 'yes' else 'No'}\n"
            f"Meal: {data.get('meal')}\n"
            f"Song Request: {data.get('song') or '—'}\n"
            f"Well Wishes: {data.get('notes') or '—'}"
        )
        msg = MIMEText(body)
        msg['Subject'] = f"New Wedding RSVP: {data.get('guest_name')}"
        msg['From'] = sender
        msg['To'] = recipient
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
        print("Email notification failed:", e)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    d = request.json
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO guests (name, attendance, meal, song, notes) VALUES (%s, %s, %s, %s, %s)",
                     (d.get('guest_name'), d.get('attendance'), d.get('meal'), d.get('song'), d.get('notes')))
        conn.commit()
        cur.close()
        conn.close()
        send_rsvp_email(d)
        return jsonify({"success": True})
    except Exception as e:
        print("RSVP error:", e)
        return jsonify({"success": False}), 500

@app.route('/api/toast', methods=['POST'])
def add_toast():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE stats SET toasts = toasts + 1 WHERE id = 1')
    conn.commit()
    cur.execute('SELECT toasts FROM stats WHERE id = 1')
    res = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"toasts": res[0]})

@app.route('/api/toasts')
def get_toasts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT toasts FROM stats WHERE id = 1')
    res = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"toasts": res[0] if res else 0})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return "No file", 400
    file = request.files['file']
    if file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO memories (filename, caption) VALUES (%s, %s)", (filename, ""))
        conn.commit()
        cur.close()
        conn.close()
    return jsonify({"success": True})

@app.route('/api/memories')
def get_memories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM memories ORDER BY id DESC")
    mems = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"filename": m[0]} for m in mems])

@app.route('/api/songs')
def get_songs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, song FROM guests WHERE song != '' ORDER BY id DESC")
    songs = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"name": s[0], "song": s[1]} for s in songs])

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
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM guests")
    guests = cur.fetchall()
    cur.execute('SELECT toasts FROM stats WHERE id = 1')
    toasts = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('admin.html', guests=guests, toasts=toasts)

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
