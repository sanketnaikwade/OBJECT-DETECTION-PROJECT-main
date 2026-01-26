# Technical Implementation Details

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           Object Detection Main Process                │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Video Input (Webcam or Video File)               │  │
│  └──────────┬───────────────────────────────────────┘  │
│             │                                            │
│             ▼                                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ YOLOv8 Object Detection Model                    │  │
│  └──────────┬───────────────────────────────────────┘  │
│             │                                            │
│    ┌────────┴────────┐                                 │
│    │                 │                                 │
│    ▼                 ▼                                 │
│ Distance         Store in                             │
│ Calculation   current_detections                     │
│    │                 │                                 │
│    └────────┬────────┘                                 │
│             │                                            │
│    ┌────────┴────────────────────────────────────┐    │
│    │                                              │    │
│    ▼                                              ▼    │
│ Announce via                              Listen for   │
│ Text-to-Speech                            Questions    │
│ (Thread 1)                            (Thread 2)       │
│    │                                      │             │
│    │                          ┌───────────┘             │
│    │                          │                         │
│    │                          ▼                         │
│    │              ┌──────────────────────┐             │
│    │              │ Generate Answer from │             │
│    │              │ current_detections   │             │
│    │              └──────────┬───────────┘             │
│    │                         │                         │
│    └─────────────┬───────────┘                         │
│                  │                                      │
│                  ▼                                      │
│         Speak Answer via TTS                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Object Detection Engine

- **Model**: YOLOv8 nano (yolov8n.pt)
- **Confidence threshold**: 0.4 (40%)
- **Input resolution**: 480x640
- **Performance**: ~50-60ms per frame

### 2. Distance Calculation

```python
distance = (frame_width * 0.5) / tan(35°) / (object_width)
```

- Uses pinhole camera model
- Adjusts for object class average widths
- Returns distance in meters

### 3. Position Detection

- **Left**: x < frame_width / 3
- **Center**: frame_width / 3 ≤ x < 2 \* frame_width / 3
- **Right**: x ≥ 2 \* frame_width / 3

### 4. Speech Recognition

- **Engine**: Google Speech Recognition (via SpeechRecognition library)
- **Timeout**: 5 seconds per query
- **Language**: English (configurable)
- **Energy threshold**: 4000 (for ambient noise adjustment)

### 5. Text-to-Speech

- **Engine**: pyttsx3 (offline, cross-platform)
- **Speech rate**: 235 WPM (words per minute)
- **Volume**: 1.0 (maximum)

## Threading Model

```
Main Thread:
  ├─ Initialize Components
  ├─ Load YOLOv8 Model
  ├─ Create Child Threads
  └─ Main Detection Loop
      ├─ Read Frame
      ├─ Run Inference
      ├─ Update current_detections[]
      ├─ Add to announcement queue
      └─ Display Annotated Frame

Thread 1 (Announcements):
  └─ Continuously Monitor queue
     ├─ Fetch detection
     ├─ Generate audio text
     └─ Speak via TTS

Thread 2 (Question Answering):
  └─ Continuously Listen via Microphone
     ├─ Capture Audio
     ├─ Convert Speech to Text
     ├─ Call generate_answer()
     ├─ Generate Response
     └─ Speak Answer via TTS
```

## Question Processing Logic

The `generate_answer()` function uses pattern matching:

```python
# Pattern Priority:
1. "what" + ("see"|"detect"|"around") → List all objects
2. "how many" → Count total objects
3. "nearest"|"closest" → Find min distance object
4. "left" → Filter objects by position
5. "right" → Filter objects by position
6. "center" → Filter objects by position
7. "front"|"ahead" → List all objects ahead
8. Default → Return generic response with detections
```

## Data Structures

### Detection Dictionary

```python
{
    'label': 'person',           # Object class name
    'distance': 2.5,             # Distance in meters
    'position': 'center',        # left|center|right
    'coords': [x1, y1, x2, y2]  # Bounding box
}
```

### Global State

```python
current_detections = []          # List of current detections
last_spoken = {}                 # Cooldown tracking
last_distances = {}              # Previous distances
speech_cooldown = 5              # Seconds between announcements
```

## Performance Metrics

- **Detection Latency**: ~56ms per frame
- **Preprocessing**: ~1.5ms
- **Inference**: ~54ms
- **Postprocessing**: ~1ms
- **Speech Recognition**: ~500-2000ms (network-dependent)
- **TTS Generation**: ~500-1000ms per sentence

## Supported YOLOv8 Classes (80 Total)

Person, Bicycle, Car, Motorcycle, Airplane, Bus, Train, Truck, Boat, Traffic Light, Fire Hydrant, Stop Sign, Parking Meter, Bench, Cat, Dog, Horse, Sheep, Cow, Elephant, Bear, Zebra, Giraffe, Backpack, Umbrella, Handbag, Tie, Suitcase, Frisbee, Skis, Snowboard, Sports Ball, Kite, Baseball Bat, Baseball Glove, Skateboard, Surfboard, Tennis Racket, Bottle, Wine Glass, Cup, Fork, Knife, Spoon, Bowl, Banana, Apple, Sandwich, Orange, Broccoli, Carrot, Hot Dog, Pizza, Donut, Cake, Chair, Couch, Potted Plant, Bed, Dining Table, Toilet, TV, Laptop, Mouse, Remote, Keyboard, Microwave, Oven, Toaster, Sink, Refrigerator, Book, Clock, Vase, Scissors, Teddy Bear, Hair Drier, Toothbrush

## Configuration Parameters

| Parameter           | Current Value | Purpose                                   |
| ------------------- | ------------- | ----------------------------------------- |
| `conf`              | 0.4           | Detection confidence threshold            |
| `speech_cooldown`   | 5             | Seconds between same-object announcements |
| `energy_threshold`  | 4000          | Microphone sensitivity                    |
| `listen_timeout`    | 5             | Seconds to listen for question            |
| `distance_limit`    | 12            | Meters threshold for announcements        |
| `blur_height_ratio` | 0.08          | Face blur size (% of person height)       |
| `speech_rate`       | 235           | Words per minute                          |
| `volume`            | 1.0           | Speaker volume (0.0-1.0)                  |

## Privacy Considerations

- Person faces are blurred in video output (80% of face height)
- No data logging or transmission
- All processing is local
- Video saved to disk for review only

## Error Handling

1. **Speech Recognition Errors**
   - `UnknownValueError`: "Could not understand the question"
   - `RequestError`: "Could not request results"

2. **Microphone Errors**
   - Detected automatically
   - Retries with 1-second delay

3. **Detection Errors**
   - Graceful degradation if model fails
   - Continues processing next frame

## Extension Points

### Add Custom Answer Logic

Extend the `generate_answer()` function:

```python
elif "your_keyword" in question_lower:
    # Your custom logic here
    return "Your answer"
```

### Add Gesture Recognition

Integrate additional models for hand/body pose detection

### Add Language Support

Modify recognizer language:

```python
question = recognizer.recognize_google(audio, language='es-ES')
```

### Add Haptic Feedback

Integrate with device vibration API for proximity alerts

### Add AI-Powered Answers

Uncomment Google Generative AI integration for complex reasoning:

```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
```

## System Requirements

- **CPU**: Intel i5 or equivalent (minimum)
- **RAM**: 4GB minimum, 8GB recommended
- **Microphone**: USB microphone recommended
- **Camera/Webcam**: HD resolution (720p+)
- **Python**: 3.8+
- **OS**: Windows, Linux, macOS

## Dependency Graph

```
pyttsx3 (TTS)
SpeechRecognition (Speech input)
  └─ pyaudio (microphone access)
ultralytics (YOLOv8)
  └─ torch (deep learning)
  └─ opencv-python (image processing)
    └─ numpy (numerical computing)
```
