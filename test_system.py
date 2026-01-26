#!/usr/bin/env python3
"""
Test script to verify all components of the voice assistant are working correctly.
Run this before using the main application.
"""

import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    packages = {
        'pyttsx3': 'Text-to-Speech',
        'speech_recognition': 'Speech Recognition',
        'ultralytics': 'YOLOv8 Detection',
        'cv2': 'OpenCV',
        'numpy': 'NumPy'
    }
    
    all_good = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"  [OK]   {package:30} ({description})")
        except ImportError:
            print(f"  [FAIL] {package:30} ({description}) - MISSING!")
            all_good = False
    
    return all_good

def test_tts():
    """Test text-to-speech functionality"""
    print("\nTesting Text-to-Speech...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("Text to speech is working")
        engine.runAndWait()
        print("  [OK]   TTS working correctly")
        return True
    except Exception as e:
        print(f"  [FAIL] TTS Error: {e}")
        return False

def test_microphone():
    """Test microphone access"""
    print("\nTesting Microphone...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
        print("  [OK]   Microphone detected and working")
        return True
    except Exception as e:
        print(f"  [FAIL] Microphone Error: {e}")
        return False

def test_yolo_model():
    """Test YOLO model loading"""
    print("\nTesting YOLOv8 Model...")
    try:
        from ultralytics import YOLO
        print("  [INFO] Attempting to load YOLOv8 nano model...")
        print("    (First time may take a minute to download model)")
        model = YOLO('yolov8n.pt')
        print("  [OK]   YOLOv8 model loaded successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] YOLOv8 Error: {e}")
        return False

def test_question_answering():
    """Test question answering logic"""
    print("\nTesting Question Answering Logic...")
    try:
        # Simulate detections
        sample_detections = [
            {'label': 'person', 'distance': 2.5, 'position': 'center', 'coords': [100, 100, 200, 200]},
            {'label': 'car', 'distance': 5.0, 'position': 'left', 'coords': [50, 50, 150, 150]},
            {'label': 'dog', 'distance': 1.5, 'position': 'right', 'coords': [300, 300, 400, 400]},
        ]
        
        # Test questions
        test_questions = [
            "What do you see?",
            "How many objects?",
            "What's nearest?",
            "What's on my left?",
            "What's on my right?",
        ]
        
        # Import the function from main.py
        sys.path.insert(0, '.')
        from main import generate_answer
        
        for question in test_questions:
            answer = generate_answer(question, sample_detections)
            print(f"  Q: {question}")
            print(f"  A: {answer}")
        
        print("  [OK]   Question answering working correctly")
        return True
    except Exception as e:
        print(f"  [FAIL] Question Answering Error: {e}")
        return False

def test_camera():
    """Test camera/webcam access"""
    print("\nTesting Camera/Webcam...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f"  [OK]   Camera working (Frame: {frame.shape})")
                return True
        print("  [FAIL] Camera not accessible (may be in use or unavailable)")
        return False
    except Exception as e:
        print(f"  [FAIL] Camera Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Voice Assistant - System Test Suite")
    print("=" * 60)
    
    results = {
        'Imports': test_imports(),
        'Text-to-Speech': test_tts(),
        'Microphone': test_microphone(),
        'YOLOv8 Model': test_yolo_model(),
        'Question Answering': test_question_answering(),
        'Camera/Webcam': test_camera(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} {status}")
    
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[OK] All systems ready! You can now run: python main.py")
    else:
        print("\n[FAIL] Some systems need attention. Please fix errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
