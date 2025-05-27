import paramiko
import datetime
import os
import cv2
import argparse
import zipfile

def main():
    parser = argparse.ArgumentParser(description="Autodarts Log & Bild Grabber")
    parser.add_argument("--host", required=True, help="Hostname oder IP des Servers")
    parser.add_argument("--username", required=True, help="SSH Benutzername")
    parser.add_argument("--password", required=True, help="SSH Passwort")
    args = parser.parse_args()

    HOST = args.host
    USERNAME = args.username
    PASSWORD = args.password

    # SSH-Verbindung herstellen
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
    except Exception as e:
        print(f"Verbindung fehlgeschlagen: {e}")
        return

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

    print(f"Log gespeichert in: {filepath}")

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
            print(f"Bild gespeichert in: {out_path}")
        else:
            print(f"Kein Bild aus dem Stream {url_http} erhalten.")
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
    print(f"Alle Dateien als ZIP gespeichert: {zip_filepath}")

if __name__ == "__main__":
    main()