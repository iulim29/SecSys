import time

alerts = []
last_alert_time = {}
cooldown_seconds = 10  # per-camera cooldown

def log_alert(cam_id="Unknown", snapshot_path=None):
    global last_alert_time
    now = time.time()

    # Initialize per-camera cooldown
    if cam_id not in last_alert_time:
        last_alert_time[cam_id] = 0

    if now - last_alert_time[cam_id] < cooldown_seconds:
        return

    last_alert_time[cam_id] = now
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"Person detected on {cam_id.upper()}"

    alert = {
        "message": message,
        "timestamp": timestamp,
    }

    if snapshot_path:
        alert["image"] = snapshot_path  # relative path to snapshot

    alerts.append(alert)
    print(f"[ALERT] {message} at {timestamp}")

def get_alerts():
    return alerts[-50:]  # optional: keep latest 50
