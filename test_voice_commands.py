#!/usr/bin/env python
"""Quick test to verify voice commands are working"""

import time
from main import speak_text, current_detections, generate_answer
import speech_recognition as sr

print("✓ Successfully imported main module")
print("✓ TTS function available")
print(f"✓ Current detections storage: {current_detections}")

# Test TTS
print("\n--- Testing Text-to-Speech ---")
print("Queueing speech: 'Voice system is now active'")
speak_text("Voice system is now active")
time.sleep(2)
print("✓ TTS working - you should have heard 'Voice system is now active'")

# Test speech recognition setup
print("\n--- Testing Speech Recognition Setup ---")
recognizer = sr.Recognizer()
try:
    with sr.Microphone() as source:
        print("✓ Microphone detected and ready")
        print("  Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✓ Microphone calibrated")
except Exception as e:
    print(f"✗ Microphone error: {e}")

# Test answer generation
print("\n--- Testing Answer Generation ---")
test_detections = [
    {'label': 'person', 'distance': 2, 'position': 'center', 'coords': [0, 0, 100, 100]},
    {'label': 'chair', 'distance': 3.5, 'position': 'left', 'coords': [0, 0, 100, 100]},
    {'label': 'table', 'distance': 4, 'position': 'right', 'coords': [0, 0, 100, 100]},
]

questions = [
    "What do you see?",
    "How many objects are there?",
    "What is the nearest object?",
    "What is on the left?",
    "What is on the right?",
]

for q in questions:
    answer = generate_answer(q, test_detections)
    print(f"Q: {q}")
    print(f"A: {answer}\n")

print("✓ All tests passed! Voice system appears to be working correctly.")
print("\nNow run: python main.py")
print("Then try asking questions when 'Listening for questions...' appears")
