import paramiko
import datetime
import os
import cv2
import zipfile
from flask import Flask, render_template_string, request, send_file, session
import threading

app = Flask(__name__)
app.secret_key = "05184711-1337-7331-11748150"

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Autodarts Log & Bild Grabber</title>
    <style>
        body {
            background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #fff;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        .container {
            background: rgba(30, 60, 120, 0.85);
            max-width: 400px;
            margin: 60px auto 0 auto;
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            padding: 32px 32px 24px 32px;
        }
        h2 {
            text-align: center;
            margin-bottom: 28px;
            color: #bbdefb;
            letter-spacing: 1px;
        }
        label {
            display: block;
            margin-bottom: 12px;
            color: #e3f2fd;
            font-weight: 500;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 8px 10px;
            margin-top: 4px;
            margin-bottom: 18px;
            border: none;
            border-radius: 6px;
            background: #e3f2fd;
            color: #0d47a1;
            font-size: 1em;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #1565c0;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 8px;
        }
        button:hover {
            background: #0d47a1;
        }
        .download-link {
            display: block;
            margin: 24px auto 0 auto;
            text-align: center;
            background: #64b5f6;
            color: #0d47a1;
            padding: 10px 0;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            width: 100%;
            transition: background 0.2s;
        }
        .download-link:hover {
            background: #1976d2;
            color: #fff;
        }
        .error {
            background: #e57373;
            color: #fff;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 16px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Autodarts detection log collector</h2>
        <form method="post" action="/collect">
            <label>SSH Host:
                <input type="text" name="host" value="{{ host }}" required>
            </label>
            <label>SSH Username:
                <input type="text" name="username" value="{{ username }}" required>
            </label>
            <label>SSH Password:
                <input type="password" name="password" value="{{ password }}" required>
            </label>
            <button type="submit">Collect</button>
        </form>
        {% if zipfile %}
            <a class="download-link" href="{{ url_for('download', filename=zipfile) }}">ZIP herunterladen</a>
        {% endif %}
    </div>
</body>
</html>
"""

def collect_data(HOST, USERNAME, PASSWORD):
    # SSH-Verbindung herstellen
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
    except Exception as e:
        return None, f"Verbindung fehlgeschlagen: {e}"

    # journalctl Befehl ausführen
    stdin, stdout, stderr = ssh.exec_command("journalctl -u autodarts -n 20")
    output = stdout.read().decode()
    ssh.close()

    # Dateiname mit aktuellem Datum und Uhrzeit
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{now}.txt"
    filepath = os.path.join(os.getcwd(), filename)

    # In Datei schreiben
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)

    # Hilfsfunktion für Bild-Download
    def grab_image(url_http, url_https, out_path):
        cap = cv2.VideoCapture(url_http)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            cap = cv2.VideoCapture(url_https)
            ret, frame = cap.read()
        if ret:
            cv2.imwrite(out_path, frame)
        cap.release()

    # Bild 1: detection
    stream_url_http = f"http://{HOST}:3180/api/streams/detection"
    stream_url_https = f"https://{HOST}:3180/api/streams/detection"
    image_filename = f"{now}_detection.jpg"
    image_filepath = os.path.join(os.getcwd(), image_filename)
    grab_image(stream_url_http, stream_url_https, image_filepath)

    # Bild 2: live
    live_url_http = f"http://{HOST}:3180/api/streams/live"
    live_url_https = f"https://{HOST}:3180/api/streams/live"
    live_image_filename = f"{now}_live.jpg"
    live_image_filepath = os.path.join(os.getcwd(), live_image_filename)
    grab_image(live_url_http, live_url_https, live_image_filepath)

    # ZIP-Archiv erstellen
    zip_filename = f"{now}.zip"
    zip_filepath = os.path.join(os.getcwd(), zip_filename)
    with zipfile.ZipFile(zip_filepath, "w") as zipf:
        zipf.write(filepath, arcname=filename)
        zipf.write(image_filepath, arcname=image_filename)
        zipf.write(live_image_filepath, arcname=live_image_filename)

    # Aufräumen der Einzeldateien (optional)
    os.remove(filepath)
    os.remove(image_filepath)
    os.remove(live_image_filepath)

    return zip_filename, None

@app.route("/", methods=["GET"])
def index():
    return render_template_string(
        HTML,
        zipfile=None,
        host=session.get("host", ""),
        username=session.get("username", ""),
        password=session.get("password", "")
    )

@app.route("/collect", methods=["POST"])
def collect():
    host = request.form["host"]
    username = request.form["username"]
    password = request.form["password"]
    # Werte in der Session speichern
    session["host"] = host
    session["username"] = username
    session["password"] = password
    zipfile_name, error = collect_data(host, username, password)
    if error:
        return f"<p>{error}</p><p><a href='/'>Zurück</a></p>"
    return render_template_string(
        HTML,
        zipfile=zipfile_name,
        host=host,
        username=username,
        password=password
    )

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(os.getcwd(), filename), as_attachment=True)

def run_flask():
    # Port 49152–65535 sind selten genutzt, z.B. 54321
    app.run(host="0.0.0.0", port=54321, debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()