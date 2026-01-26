import pyttsx3
from threading import Thread, Lock
from queue import Queue
from ultralytics import YOLO
import cv2
import numpy as np
import time
import sys
import speech_recognition as sr

USE_DISPLAY = True

# ================= OCR =================
try:
    import easyocr
    OCR_AVAILABLE = True
    print("[INFO] EasyOCR available")
except:
    OCR_AVAILABLE = False
    print("[WARN] EasyOCR not installed")

MODEL_PATH = "yolov8n.pt"
CURRENCY_MODEL_PATH = "currency_model.pt"   # <-- your trained currency model

# ================= TTS =================
tts_queue = Queue()

def tts_worker(q):
    import ctypes
    if sys.platform.startswith("win"):
        ctypes.windll.ole32.CoInitialize(None)

    while True:
        text = q.get()
        if text is None:
            break
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception as e:
            print("[TTS ERROR]", e)

def speak_text(text):
    if text:
        tts_queue.put(str(text))

# ================= SPEECH RECOGNITION =================
recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000
recognizer.dynamic_energy_threshold = True

announce_queue = Queue()

current_detections = []
detections_lock = Lock()

current_frame = None
frame_lock = Lock()

ocr_reader = None
if OCR_AVAILABLE:
    ocr_reader = easyocr.Reader(['en'], gpu=False)

class_avg_sizes = {
    "person": {"width_ratio": 2.5},
    "car": {"width_ratio": 0.37},
    "bicycle": {"width_ratio": 2.3},
    "motorcycle": {"width_ratio": 2.4},
    "bus": {"width_ratio": 0.3},
}

# ================= DOCUMENT DETECTION =================
def detect_document(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            return frame[y:y+h, x:x+w]

    return None

def preprocess_for_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoise = cv2.fastNlMeansDenoising(gray, h=30)
    thresh = cv2.adaptiveThreshold(
        denoise, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

# ================= OCR FUNCTION =================
def read_document(frame):
    if not OCR_AVAILABLE or ocr_reader is None:
        return "OCR not available"

    doc = detect_document(frame)
    if doc is None:
        return "No document detected. Please hold the paper in front of the camera."

    processed = preprocess_for_ocr(doc)
    results = ocr_reader.readtext(processed)

    if not results:
        return "Text not clear. Please move closer or improve lighting."

    text_lines = [txt for (_, txt, conf) in results if conf > 0.4]
    full_text = " ".join(text_lines)

    if len(full_text.strip()) == 0:
        return "Text detected but not readable."

    return full_text[:1000]

# ================= CURRENCY INTERPRETER =================
def interpret_currency(label):
    if label.startswith("INR"):
        value = label.split("_")[1]
        return f"This is an Indian {value} rupee note"
    elif label.startswith("USD"):
        value = label.split("_")[1]
        return f"This is a United States {value} dollar bill"
    elif label.startswith("EUR"):
        value = label.split("_")[1]
        return f"This is a {value} euro note"
    else:
        return f"Detected currency {label}"

# ================= Q&A =================
def generate_answer(question, detections):
    q = question.lower()

    if "what" in q and ("see" in q or "around" in q):
        if detections:
            items = list(set(d['label'] for d in detections))
            return "I see " + ", ".join(items)
        return "I see nothing"

    if "how many" in q:
        return f"I detect {len(detections)} objects"

    if "nearest" in q or "closest" in q:
        nearest = min(detections, key=lambda x: x['distance'])
        return f"Nearest object is {nearest['label']} at {nearest['distance']} meters"

    if "read" in q and ("document" in q or "text" in q):
        return "READ_DOCUMENT"

    return "Please ask about nearby objects"

# ================= ANNOUNCER THREAD =================
def speak_thread(q):
    last_spoken = {}
    cooldown = 5

    while True:
        if not q.empty():
            label, distance, position = q.get()
            now = time.time()

            if label in last_spoken and now - last_spoken[label] < cooldown:
                continue

            speak_text(f"Warning. {label} at {distance} meters on your {position}")
            last_spoken[label] = now

            while not q.empty():
                q.get()
        else:
            time.sleep(0.1)

# ================= Q&A THREAD =================
def answer_questions():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)

        while True:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                question = recognizer.recognize_google(audio)

                with detections_lock:
                    detections = current_detections.copy()

                answer = generate_answer(question, detections)

                if answer == "READ_DOCUMENT":
                    speak_text("Reading document")
                    time.sleep(1)
                    with frame_lock:
                        frame = current_frame.copy() if current_frame is not None else None
                    if frame is not None:
                        text = read_document(frame)
                        speak_text(text)
                    else:
                        speak_text("No frame available")
                else:
                    speak_text(answer)

            except sr.UnknownValueError:
                speak_text("I did not understand")
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print("[QnA ERROR]", e)

# ================= UTILS =================
def calculate_distance(box, frame_width, label):
    obj_width = box.xyxy[0][2] - box.xyxy[0][0]
    if label in class_avg_sizes:
        obj_width *= class_avg_sizes[label]["width_ratio"]
    distance = (frame_width * 0.5) / np.tan(np.radians(35)) / (obj_width + 1e-6)
    return round(float(distance), 2)

def get_position(frame_width, coords):
    x1 = coords[0]
    if x1 < frame_width // 3:
        return "left"
    elif x1 < 2 * frame_width // 3:
        return "center"
    else:
        return "right"

def blur_person(img, box):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    top = img[y1:y1 + int(0.08 * (y2 - y1)), x1:x2]
    img[y1:y1 + int(0.08 * (y2 - y1)), x1:x2] = cv2.GaussianBlur(top, (15, 15), 0)
    return img

# ================= MODELS =================
model = YOLO(MODEL_PATH)
currency_model = YOLO(CURRENCY_MODEL_PATH)

last_currency_spoken = {}
currency_cooldown = 5

# ================= MAIN =================
if __name__ == "__main__":
    Thread(target=tts_worker, args=(tts_queue,), daemon=True).start()
    Thread(target=speak_thread, args=(announce_queue,), daemon=True).start()
    Thread(target=answer_questions, daemon=True).start()

    cap = cv2.VideoCapture(0)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        with frame_lock:
            current_frame = frame.copy()

        frame_count += 1
        if frame_count % 3 != 0:
            continue

        # -------- OBJECT DETECTION --------
        results = model(frame, conf=0.4)[0]

        nearest = None
        min_dist = float('inf')

        with detections_lock:
            current_detections.clear()

            for box in results.boxes:
                label = results.names[int(box.cls[0])]
                coords = list(map(int, box.xyxy[0]))
                dist = calculate_distance(box, frame.shape[1], label)
                pos = get_position(frame.shape[1], coords)

                current_detections.append({
                    'label': label,
                    'distance': dist,
                    'position': pos
                })

                if dist < min_dist:
                    min_dist = dist
                    nearest = (label, dist, coords)

                if label == "person":
                    frame = blur_person(frame, box)
                    color = (0,255,0)
                else:
                    color = (255,0,0)

                cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), color, 2)
                cv2.putText(frame, f"{label} {dist}m",
                            (coords[0], coords[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if nearest and nearest[1] <= 12:
            pos = get_position(frame.shape[1], nearest[2])
            announce_queue.put((nearest[0], nearest[1], pos))

        # -------- CURRENCY DETECTION --------
        currency_results = currency_model(frame, conf=0.5)[0]

        for box in currency_results.boxes:
            label = currency_results.names[int(box.cls[0])]
            now = time.time()

            if label not in last_currency_spoken or now - last_currency_spoken[label] > currency_cooldown:
                msg = interpret_currency(label)
                speak_text(msg)
                last_currency_spoken[label] = now

            coords = list(map(int, box.xyxy[0]))
            cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), (255,255,0), 2)
            cv2.putText(frame, label, (coords[0], coords[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

        if USE_DISPLAY:
            try:
                cv2.imshow("Audio World", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except cv2.error:
                USE_DISPLAY = False

    cap.release()
    cv2.destroyAllWindows()
    tts_queue.put(None)
