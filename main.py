import pyttsx3
from threading import Thread, Lock
from queue import Queue
from ultralytics import YOLO
import cv2
import time
import sys
import speech_recognition as sr

MODEL_PATH = "yolov8n.pt"

model = YOLO(MODEL_PATH)

tts_queue = Queue()
is_speaking = False
speak_lock = Lock()

current_detections = []
detections_lock = Lock()

# ================= POSITION =================
def get_position(frame_width, coords):
    x1 = coords[0]
    if x1 < frame_width // 3:
        return "left"
    elif x1 < 2 * frame_width // 3:
        return "center"
    else:
        return "right"

# ================= TTS =================
def tts_worker():
    global is_speaking
    print("[OK] TTS worker started")

    while True:
        text = tts_queue.get()
        if text is None:
            break

        with speak_lock:
            is_speaking = True
            print("[SPEAK]:", text)

            try:
                engine = pyttsx3.init(driverName="sapi5")
                engine.setProperty("rate", 170)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print("[TTS ERROR]", e)

            is_speaking = False

def speak_text(text):
    if text:
        tts_queue.put(str(text))

# ================= SPEECH =================
recognizer = sr.Recognizer()

def voice_thread():
    global is_speaking
    print("[INFO] Mic initializing...")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("[OK] Mic ready")

        while True:
            try:
                while is_speaking:
                    time.sleep(0.1)

                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
                question = recognizer.recognize_google(audio)

                print("[USER]:", question)

                with detections_lock:
                    detections = current_detections.copy()

                answer = generate_answer(question, detections)
                speak_text(answer)

            except sr.UnknownValueError:
                pass
            except Exception as e:
                print("[VOICE ERROR]", e)

# ================= Q&A =================
def generate_answer(question, detections):
    q = question.lower()

    if "left" in q:
        objs = [d["label"] for d in detections if d["position"] == "left"]
        return "On your left I see " + ", ".join(set(objs)) if objs else "Nothing on your left"

    if "right" in q:
        objs = [d["label"] for d in detections if d["position"] == "right"]
        return "On your right I see " + ", ".join(set(objs)) if objs else "Nothing on your right"

    if any(w in q for w in ["front", "ahead", "center"]):
        objs = [d["label"] for d in detections if d["position"] == "center"]
        return "In front of you I see " + ", ".join(set(objs)) if objs else "Nothing in front"

    if any(w in q for w in ["nearest", "closest", "near"]):
        if detections:
            nearest = min(detections, key=lambda x: x["distance"])
            return f"Nearest object is {nearest['label']} at {nearest['distance']} meters"
        return "No nearby objects"

    if any(w in q for w in ["what", "see", "around"]):
        if detections:
            labels = list(set(d["label"] for d in detections))
            return "I see " + ", ".join(labels)
        return "I see nothing"

    return "Please ask about your surroundings"

# ================= DISTANCE =================
def calculate_distance(box, frame_width):
    obj_width = float(box.xyxy[0][2] - box.xyxy[0][0])
    return round((frame_width * 0.5) / (obj_width + 1e-6), 2)

# ================= MAIN =================
if __name__ == "__main__":
    Thread(target=tts_worker, daemon=True).start()
    Thread(target=voice_thread, daemon=True).start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    print("[INFO] Camera running")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=0.4)[0]

        with detections_lock:
            current_detections.clear()

            for box in results.boxes:
                label = results.names[int(box.cls[0])]
                coords = list(map(int, box.xyxy[0]))
                dist = calculate_distance(box, frame.shape[1])
                pos = get_position(frame.shape[1], coords)

                current_detections.append({
                    "label": label,
                    "distance": dist,
                    "position": pos
                })

        time.sleep(0.03)

    cap.release()
    tts_queue.put(None)
