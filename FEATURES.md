# Object Detection Project - Voice Assistant Features

## New Features Added

### 1. **Real-time Object Detection with Audio Feedback**

The system announces detected objects and their distances in real-time using text-to-speech.

### 2. **Speech Recognition and Question Answering**

Users (including blind individuals) can now ask questions, and the system will provide answers based on the currently detected objects.

## Supported Questions

The system can answer the following types of questions:

### General Detection Questions

- **"What do you see?"** - Lists all detected objects around the user
- **"What's around me?"** - Same as above
- **"What do you detect?"** - Same as above

### Count Questions

- **"How many objects?"** - Returns the total count of detected objects
- **"How many things?"** - Same as above

### Proximity Questions

- **"What's nearest?"** - Identifies the closest object
- **"What's closest?"** - Same as above

### Directional Questions

- **"What's on my left?"** - Lists objects detected on the left side
- **"What's on my right?"** - Lists objects detected on the right side
- **"What's in the center?"** - Lists objects in the center
- **"What's ahead?"** - Lists objects ahead
- **"What's in front?"** - Same as above

## How to Use

### Running the Application

```bash
python main.py
```

### Input Modes

When prompted, select:

- **Option 1**: Real-time Webcam input
- **Option 2**: Pre-recorded Video file

### Controls During Runtime

- **'q' key**: Quit the application
- **'p' key**: Pause/Resume video

### Asking Questions

The system continuously listens for audio input. Simply speak a question when prompted:

- Questions should be clear and loud enough for the microphone to pick up
- The system will process the question and provide an audio response
- Questions are processed in real-time as objects are being detected

## Installation Requirements

The following packages are automatically installed:

- `pyttsx3` - Text-to-speech engine
- `SpeechRecognition` - Speech recognition library
- `ultralytics` - YOLOv8 object detection
- `opencv-python` - Computer vision library
- `numpy` - Numerical computing

## Configuration Options

### Text-to-Speech Settings

In `main.py`, you can adjust:

- Speech rate: `engine.setProperty('rate', 235)` (lower = slower)
- Volume: `engine.setProperty('volume', 1.0)` (0.0 to 1.0)

### Speech Recognition Settings

- Energy threshold: `recognizer.energy_threshold = 4000` (higher = requires louder audio)
- Microphone timeout: `recognizer.listen(source, timeout=5)` (in seconds)

### Object Detection Settings

- Confidence threshold: `conf=0.4` in the model inference (higher = fewer detections)
- Distance limit for announcements: `if nearest and nearest[1] <= 12:` (in meters)

## Advanced Features

### Optional: Google Generative AI Integration

To enable more advanced question answering using Google's Gemini API:

1. Uncomment the import line in `main.py`:

```python
import google.generativeai as genai
```

2. Add your API key:

```python
genai.configure(api_key="YOUR_GOOGLE_API_KEY")
```

3. Update the `generate_answer()` function to use the API for complex questions

## Detected Object Classes

The system uses YOLOv8 nano model which can detect:

- person
- car, bicycle, motorcycle, bus
- traffic lights, stop signs
- cats, dogs
- bottles, remote controls
- And many more COCO dataset classes

## Example Usage Scenarios

### Scenario 1: Blind Person Navigation

```
User: "What's around me?"
System: "I can see person, car, and traffic light around you."

User: "How far is the nearest object?"
System: "The nearest object is a person at 2.5 meters on your center, approaching."

User: "What's on my left?"
System: "On your left, I can see a car."
```

### Scenario 2: Safety Assistance

```
User: "Is there anything nearby?"
System: "I detect 3 objects around you."

User: "What's nearest?"
System: "The nearest object is a car at 1.8 meters on your left, approaching."
```

## Troubleshooting

### "Could not understand the question"

- Speak louder and clearer
- Reduce background noise
- Adjust the `energy_threshold` value

### "No audio device found"

- Check that your microphone is connected
- Ensure microphone permissions are enabled in system settings

### Speech Recognition Timeout

- The system waits 5 seconds for input. Speak within this time window
- Adjust the timeout value in the `answer_questions()` function

## Performance Notes

- Real-time detection runs at ~50-60ms per frame
- Speech recognition adds minimal latency
- Multiple objects can be tracked simultaneously
- The system maintains object distance and position information

## Future Enhancements

- Integration with Google Gemini for more intelligent responses
- Voice profiling for better recognition of specific users
- Real-time translation support
- Integration with smart home devices
- Haptic feedback for proximity alerts
