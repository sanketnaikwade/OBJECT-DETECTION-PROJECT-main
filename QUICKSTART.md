# Quick Start Guide - Voice Assistant for Blind Navigation

## Installation Setup (First Time Only)

```bash
# Navigate to project directory
cd d:\OBJECT-DETECTION-PROJECT-main

# The required packages are automatically installed when you run the project
```

## Running the Project

```bash
python main.py
```

## First Time Usage

1. **Select Input Mode**: Choose between webcam (1) or video file (2)
2. **Allow Permissions**: Grant microphone access when prompted
3. **System Startup**: You'll hear "System activated" announcement

## Voice Commands Examples

### To Ask Questions (Speak Clearly):

```
"What do you see?"
→ Response: "I can see person, car, and traffic light around you."

"How many objects?"
→ Response: "I detect 3 objects around you."

"What's nearest?"
→ Response: "The nearest object is a person at 2.5 meters on your center, approaching."

"What's on my left?"
→ Response: "On your left, I can see a car."

"What's on my right?"
→ Response: "On your right, I can see a person."

"What's in the center?"
→ Response: "In the center, I can see a traffic light."

"What's ahead?"
→ Response: "Ahead of you, I can see a person and a car."
```

## Keyboard Controls

- **'q'**: Quit the application
- **'p'**: Pause/Resume detection
- **Microphone**: Speak to ask questions anytime

## Understanding Distances

The system provides distances in meters and indicates:

- **Motion**: approaching, going away, or ahead
- **Direction**: left, center, or right
- **Proximity**: very close (≤2 meters)

## Tips for Best Results

1. **Clear Speech**: Speak clearly and at normal volume
2. **Microphone Position**: Keep microphone at arm's length
3. **Quiet Environment**: Reduce background noise for better recognition
4. **Proper Lighting**: Ensure good lighting for better object detection
5. **Device Orientation**: Face the camera/webcam toward objects

## Common Issues & Solutions

| Issue                   | Solution                     |
| ----------------------- | ---------------------------- |
| Microphone not detected | Check system audio settings  |
| "Could not understand"  | Speak louder and clearer     |
| Objects not detected    | Improve lighting, get closer |
| Timeout errors          | Speak within 5 seconds       |

## Output Files

The project creates:

- `output_with_boxes.avi` - Video with detection boxes

## What Objects Can Be Detected?

- People (with privacy blur)
- Vehicles (cars, buses, bicycles, motorcycles)
- Traffic signs (stop signs, traffic lights)
- Common objects (bottles, remotes, etc.)
- Animals (cats, dogs)
- And 80+ more object classes

## Accessibility Features

✓ Text-to-speech audio output
✓ Real-time voice recognition
✓ Direction-aware object positioning
✓ Distance estimation in meters
✓ Motion tracking (approaching/going away)
✓ Motion alert (when objects get very close)

---

**Ready to start?** Run `python main.py` and ask "What do you see?"
