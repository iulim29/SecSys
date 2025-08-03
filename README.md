# SecSys: YOLO-Based Smart Security System

**SecSys** is an open-source, privacy-first home surveillance system using a custom-trained YOLOv8 model for real-time person detection. It runs entirely on local hardware (e.g. an old laptop with GPU support) and delivers push notifications via Firebase when intrusions are detected.

## 🔍 Features

- 🧠 Real-time person detection using YOLOv8n  
- 📷 Dual camera support (internal + USB)  
- 📤 Push alerts via Firebase Cloud Messaging  
- 🔐 Fully local networking via Tailscale (no port forwarding required)  
- 🌐 Flask-based web UI (snapshots, logs, and live MJPEG streams)  
- 📱 Flutter mobile app with embedded web interface  

## 🧱 Architecture

The system includes the following components:

- **Backend:** Python + Flask server for video processing and alert management.  
- **Detection:** YOLOv8n model with confidence thresholding and alert debouncing.  
- **Notifications:** Firebase Cloud Messaging for real-time alerts.  
- **Mobile App:** Flutter app using WebView + Firebase integration.  
- **Networking:** Tailscale for secure peer-to-peer access.  

## 🚀 Getting Started

1. **Clone this repo locally**
   ```bash
   git clone https://github.com/iulim29/SecSys.git
   cd SecSys
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the YOLOv8 model**
   Place your custom or pretrained `yolov8n.pt` checkpoint in the root folder.

4. **Set up Firebase credentials**
   Add your Firebase `credentials.json` and hardcode the mobile FCM token in the backend config.

5. **Run the server**
   ```bash
   python unified_app_2cam.py
   ```

6. **Access via Tailscale IP**
   Open the Flask web interface in a browser or through the mobile app WebView.

## 📱 Mobile App

- Flutter-based  
- Receives push notifications using `firebase_messaging`  
- Loads the Flask UI via WebView  
- Requires the device to be in the same Tailscale network  

## 📂 Folder Structure

```
backend/
├── alerts.py
├── detection.py
├── sec_stream.py
├── unified_app_2cam.py
├── templates/
├── static/
│   └── snapshots/
└── .gitignore
```

## ⚠️ Limitations

- No night vision support (camera hardware constraint)  
- Internet is required for Firebase notifications (but not for core detection)  
- Single-user token setup (not multi-device ready)  

## 🔒 Security

- No data leaves your device  
- End-to-end encrypted networking via Tailscale  
- No reliance on third-party cloud storage  

## 📊 Performance

- Detection latency: ~1–2 seconds  
- Custom-trained YOLO model on 8,000+ person images  
- Excellent precision under good lighting conditions  

## 📸 Example Snapshots

_(Add example images here if desired)_

## 📚 References

- [YOLOv8 - Ultralytics](https://docs.ultralytics.com/models/yolov8/)  
- [Flask](https://flask.palletsprojects.com/)  
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)  
- [Tailscale](https://tailscale.com/)  
- [Flutter](https://flutter.dev/)  

---

**Author**: Ioan-Iulian Moldovan  
Technical University of Cluj-Napoca  
[iulianmoldovan162@gmail.com](mailto:iulianmoldovan162@gmail.com)
