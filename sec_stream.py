import cv2

for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Force DirectShow
    if cap.read()[0]:
        print(f"[DSHOW] Camera {i} is working.")
        cap.release()
    else:
        print(f"[DSHOW] Camera {i} not available.")
