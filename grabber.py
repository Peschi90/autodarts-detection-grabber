import paramiko
import datetime
import os
import cv2
import argparse

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

    # Bild herunterladen
    stream_url_http = f"http://{HOST}:3180/api/streams/detection"
    stream_url_https = f"https://{HOST}:3180/api/streams/detection"
    image_filename = f"{now}.jpg"
    image_filepath = os.path.join(os.getcwd(), image_filename)
    try:
        cap = cv2.VideoCapture(stream_url_http)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            cap = cv2.VideoCapture(stream_url_https)
            ret, frame = cap.read()
        if ret:
            cv2.imwrite(image_filepath, frame)
            print(f"Bild gespeichert in: {image_filepath}")
        else:
            print("Kein Bild aus dem Stream erhalten.")
        cap.release()
    except Exception as e:
        print(f"Bild konnte nicht geladen werden: {e}")

if __name__ == "__main__":
    main()