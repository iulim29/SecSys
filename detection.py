import cv2
import time
from ultralytics import YOLO
from alerts import log_alert



def run_detection():
    model = YOLO('yolo11n.pt')
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    last_alert_time = 0
    cooldown_seconds = 30
    person_present = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False, conf=0.6)  # or 0.7 for stricter detection
        person_detected = any(int(cls) == 0 and conf > 0.6 for cls, conf in zip(results[0].boxes.cls, results[0].boxes.conf))

        now = time.time()

        if person_detected and not person_present:
            if now - last_alert_time > cooldown_seconds:
                log_alert()
                last_alert_time = now
                cv2.imwrite("static/snapshot.jpg", frame)
            person_present = True
        elif not person_detected:
            person_present = False

        annotated_frame = results[0].plot()
        label = "Person detected" if person_detected else "No person"
        cv2.putText(annotated_frame, label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0) if person_detected else (0, 0, 255), 2)

        cv2.imshow("YOLO Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
