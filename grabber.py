import paramiko
import datetime
import os
import cv2
import zipfile
from flask import Flask, render_template, request, send_file, session
import threading

app = Flask(__name__)
app.secret_key = "05184711-1337-7331-11748150"

def collect_data(HOST, USERNAME, PASSWORD):
    # SSH-Verbindung herstellen
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
    except Exception as e:
        return None, f"Verbindung fehlgeschlagen: {e}"

    # journalctl Befehl ausführen
    stdin, stdout, stderr = ssh.exec_command("journalctl -u autodarts -n 25")
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
    return render_template(
        "index.html",
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
    return render_template(
        "index.html",
        zipfile=zipfile_name,
        host=host,
        username=username,
        password=password
    )

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(os.getcwd(), filename), as_attachment=True)

def run_flask():
    # Port 54321 ist selten belegt
    app.run(host="0.0.0.0", port=54321, debug=False)

if __name__ == "__main__":
    # Flask im Hauptthread starten (kein threading nötig)
    run_flask()