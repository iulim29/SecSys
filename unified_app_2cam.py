import cv2
import time
import threading
from flask import Flask, render_template, Response, request, send_file, abort, redirect, url_for, session
from ultralytics import YOLO
from alerts import log_alert, get_alerts
import numpy as np
from datetime import timedelta
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, messaging

# Load .env config
load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
FLASK_SECRET = os.getenv("FLASK_SECRET")

# Firebase setup
cred = credentials.Certificate("secsys-5cb33-firebase-adminsdk-fbsvc-6143228655.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.secret_key = FLASK_SECRET
app.permanent_session_lifetime = timedelta(minutes=5)

# =========================
# Camera State Management
# =========================

detection_status = {
    "cam1": {"frame": None, "lock": threading.Lock(), "active": False, "last_alert": 0},
    "cam2": {"frame": None, "lock": threading.Lock(), "active": False, "last_alert": 0},
}

# =========================
# Shared Functions
# =========================

def send_push_notification(fcm_token, cam_id="Unknown"):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=f'🚨 Person Detected on {cam_id.upper()}!',
                body='Motion has been detected by SecSys.',
            ),
            token=fcm_token,
        )
        response = messaging.send(message)
        print(f"[FCM] ✅ Notification sent: {response}")
    except Exception as e:
        print(f"[FCM] ❌ Failed to send notification: {e}")


def start_detection_thread(cam_id, cam_index, fcm_token):
    def detect():
        model = YOLO("yolov8n.pt")
        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print(f"[ERROR] Failed to open camera {cam_id}")
            return

        person_present = False
        cooldown_seconds = 7
        last_alert_time = 0
        no_person_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            results = model(frame, verbose=False, conf=0.6)
            annotated = results[0].plot()

            with detection_status[cam_id]["lock"]:
                detection_status[cam_id]["frame"] = annotated.copy()

            # Detection logic
            person_detected = any(
                int(cls) == 0 and conf > 0.6
                for cls, conf in zip(results[0].boxes.cls, results[0].boxes.conf)
            )

            if person_detected:
                detection_status[cam_id]["active"] = True
                if not person_present and (time.time() - last_alert_time > cooldown_seconds):
                    cv2.imwrite(f"static/snapshot_{cam_id}.jpg", frame)

                    # Also save a timestamped version for alert history
                    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                    snapshot_path = f"static/snapshots/{cam_id}_{timestamp}.jpg"
                    os.makedirs("static/snapshots", exist_ok=True)
                    cv2.imwrite(snapshot_path, frame)

                    # Log alert with path to saved snapshot
                    log_alert(cam_id, snapshot_path=snapshot_path)

                    threading.Thread(target=send_push_notification, args=(fcm_token, cam_id)).start()


                person_present = True
                no_person_frames = 0
            else:
                no_person_frames += 1
                if no_person_frames > 5:
                    person_present = False
                    detection_status[cam_id]["active"] = False

            time.sleep(0.05)

    threading.Thread(target=detect, daemon=True).start()


def generate_frames(cam_key):
    while detection_status[cam_key]["frame"] is None:
        time.sleep(0.1)
    while True:
        with detection_status[cam_key]["lock"]:
            frame_copy = detection_status[cam_key]["frame"].copy()
        ret, buffer = cv2.imencode('.jpg', frame_copy)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# =========================
# Session / Auth
# =========================

def is_authenticated():
    if session.get("authenticated"):
        now = time.time()
        if now - session.get("last_active", now) > 300:
            session.clear()
            return False
        session['last_active'] = now
        return True
    return False

@app.before_request
def update_last_active():
    if session.get("authenticated"):
        session['last_active'] = time.time()

# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    key = request.form.get('key')
    if key == ACCESS_KEY:
        session['authenticated'] = True
        session['last_active'] = time.time()
        return redirect('/select_camera')
    return render_template("login.html", error="Invalid key!")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/select_camera')
def select_camera():
    if not is_authenticated():
        return redirect('/')
    return render_template("camera_selector.html", status=detection_status)

@app.route('/video_feed/<cam_id>')
def video_feed(cam_id):
    if not is_authenticated() or cam_id not in detection_status:
        abort(403)
    return Response(generate_frames(cam_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    if not is_authenticated():
        abort(403)
    return {
        cam: {"active": data["active"]}
        for cam, data in detection_status.items()
    }

@app.route('/alerts')
def alerts():
    return render_template("alerts.html", alerts=get_alerts())

@app.route('/stream')
def stream_page():
    if not is_authenticated():
        return redirect('/')
    
    cam_id = request.args.get("cam", "cam1")
    if cam_id not in detection_status:
        cam_id = "cam1"

    return render_template("stream.html", key=ACCESS_KEY, cam_id=cam_id)

@app.route('/snapshot/<cam_id>')
def snapshot(cam_id):
    if cam_id not in detection_status:
        abort(404)
    return send_file(f"static/snapshot_{cam_id}.jpg", mimetype='image/jpeg')




# =========================
# MAIN
# =========================
FCM_TOKEN = "fOXgah8fQ9KHjcjdr3V1K-:APA91bEjturdGFV3rAFSDQtbh-FUGoDBpDKtfyl3CHDYsKG9HSLOaMJQ3dXYwq7en5x5TzOi1MY6RkVu8ZPE5ZxZgDlX2gqrQ6lKfB-qRgTkwzY-lBpaRQE"
if __name__ == "__main__":
    start_detection_thread("cam1", 0, FCM_TOKEN)
    start_detection_thread("cam2", 1, FCM_TOKEN)

    app.run(host='0.0.0.0', port=8080)