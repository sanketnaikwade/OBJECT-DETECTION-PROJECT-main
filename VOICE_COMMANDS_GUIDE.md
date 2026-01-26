# Voice Commands - Quick Start Guide

## How to Use Voice Commands

### Step 1: Start the Application

```bash
python main.py
```

### Step 2: Select Input Mode

Choose between:

- **Option 1**: Real-time Webcam (live camera feed)
- **Option 2**: Pre-recorded Video (test video file)

### Step 3: Use Voice Commands

The system will announce detected objects automatically. When you hear **"Listening for questions... (speak now)"**, you can ask questions!

## Supported Question Types

### 1. **"What do you see?" or similar**

- Patterns: "what see", "what detect", "what around", "what's nearby"
- Response: Lists all detected objects

### 2. **"How many objects?"**

- Patterns: "how many"
- Response: Total count of detected objects

### 3. **"What is nearest?" or "Closest object?"**

- Patterns: "nearest", "closest", "near"
- Response: Nearest object with exact distance

### 4. **"What's on the left?"**

- Patterns: "left", "left side", "my left"
- Response: Objects on the left side with distances

### 5. **"What's on the right?"**

- Patterns: "right", "right side", "my right"
- Response: Objects on the right side with distances

### 6. **"What's in the center?"**

- Patterns: "center", "center view", "middle"
- Response: Objects in the center region

### 7. **"What's ahead?" or "What's in front?"**

- Patterns: "front", "ahead", "forward"
- Response: Objects directly in front

## Example Questions You Can Ask

```
"What do you see?"
"How many objects are around me?"
"What is the nearest object?"
"What's on my left?"
"What's on my right?"
"What's in the center?"
"What's ahead of me?"
"What else is nearby?"
"How many people are there?"
"Tell me what objects are detected"
```

## Keyboard Controls

- **'q'**: Quit the application
- **'p'**: Pause/Resume video

## Troubleshooting

### "I don't hear the listening prompt"

- Ensure your speakers are connected and volume is up
- Wait 2-3 seconds after starting - the system needs time to initialize

### "My questions aren't being recognized"

- Speak clearly and naturally
- Make sure you ask questions about spatial information (left, right, center, etc.)
- Wait for the "Listening for questions..." message before speaking
- You have 10 seconds to ask your question (15 seconds for longer questions)

### "I'm getting no response"

- Check internet connection (Google Speech Recognition API needs it)
- Verify microphone is properly connected
- Try asking a different question pattern
- Check the console for error messages

### "Microphone not detected"

- Connect your microphone/headset
- Check Windows Sound Settings
- Restart the application
- Run `python test_voice_commands.py` to diagnose

## Tips for Best Results

1. **Speak naturally** - The system understands natural phrasing
2. **Ask location-based questions** - Focus on "where" questions (left, right, center)
3. **Minimize background noise** - Quieter environment = better recognition
4. **Use complete sentences** - "What do you see?" works better than just "see"
5. **Wait for the prompt** - Always wait for "Listening for questions..." message

## Technical Details

- **Speech Recognition**: Google Cloud Speech Recognition API
- **Voice Output**: pyttsx3 text-to-speech engine
- **Microphone Input**: System default microphone
- **Recognition Timeout**: 10 seconds per question
- **Phrase Limit**: 15 seconds for longer questions
- **Language**: English (US)

## Performance

- Object Detection: 50-60ms per frame (real-time)
- Speech Recognition: 2-5 seconds (depends on question length and internet)
- TTS Response: Immediate playback after recognition

Enjoy your voice-controlled object detection system!
