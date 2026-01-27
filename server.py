from flask import Flask, jsonify, Response
from ultralytics import YOLO
import cv2

app = Flask(__name__)
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

FOCAL_LENGTH = 700
REAL_WIDTH = 0.5  # avg object width (meters)

import easyocr
reader = easyocr.Reader(['en'])

import easyocr
reader = easyocr.Reader(['en'])

def detect_currency(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray)

    text_found = " ".join([res[1] for res in results]).lower()

    # ---------- INR ----------
    if "2000" in text_found:
        return "Two thousand rupees note"
    elif "500" in text_found:
        return "Five hundred rupees note"
    elif "200" in text_found:
        return "Two hundred rupees note"
    elif "100" in text_found:
        return "One hundred rupees note"
    elif "50" in text_found:
        return "Fifty rupees note"
    elif "20" in text_found:
        return "Twenty rupees note"
    elif "10" in text_found:
        return "Ten rupees note"

    # ---------- USD ----------
    elif "$100" in text_found or "100" in text_found and "united states" in text_found:
        return "One hundred US dollars"
    elif "$50" in text_found:
        return "Fifty US dollars"
    elif "$20" in text_found:
        return "Twenty US dollars"
    elif "$10" in text_found:
        return "Ten US dollars"
    elif "$5" in text_found:
        return "Five US dollars"

    # ---------- EURO ----------
    elif "€" in text_found or "euro" in text_found:
        if "100" in text_found:
            return "One hundred euros"
        elif "50" in text_found:
            return "Fifty euros"
        elif "20" in text_found:
            return "Twenty euros"
        elif "10" in text_found:
            return "Ten euros"
        elif "5" in text_found:
            return "Five euros"

    # ---------- POUND ----------
    elif "£" in text_found or "pound" in text_found:
        if "50" in text_found:
            return "Fifty pounds"
        elif "20" in text_found:
            return "Twenty pounds"
        elif "10" in text_found:
            return "Ten pounds"
        elif "5" in text_found:
            return "Five pounds"

    return None




@app.route("/detect")
def detect():
    ret, frame = cap.read()
    if not ret:
        return jsonify({"objects": []})

    results = model(frame)[0]
    h, w, _ = frame.shape
    detected = []

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        box_width = x2 - x1
        center_x = (x1 + x2) // 2

        distance = round((REAL_WIDTH * FOCAL_LENGTH) / box_width, 1)

        if center_x < w/3:
            position = "left"
        elif center_x > 2*w/3:
            position = "right"
        else:
            position = "front"

        detected.append(f"{label} {distance} meters {position}")

    currency = detect_currency(frame)
    if currency:
        detected.append(currency)

    return jsonify({"objects": detected})


def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)[0]
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            label = model.names[cls]
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,label,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
