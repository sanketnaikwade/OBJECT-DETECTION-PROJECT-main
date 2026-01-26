#!/usr/bin/env python
"""Quick check if easyocr is installed"""
try:
    import easyocr
    print("[OK] easyocr is installed")
except ImportError:
    print("[INFO] easyocr not installed")
    print("   Install with: pip install easyocr")
    print("   Note: First run will download models (~500MB)")
