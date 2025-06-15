"""
Test script for the Pose Analyzer API
"""

import requests
import json
import cv2
import numpy as np
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_image_analysis():
    """Test image analysis with a generated test image"""
    print("Testing image analysis...")
    
    # Create a test image (blank white image)
    test_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Add some text
    cv2.putText(test_image, "Test Image", (50, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Save temporarily
    cv2.imwrite("test_image.jpg", test_image)
    
    # Upload to API
    with open("test_image.jpg", "rb") as f:
        files = {"file": ("test_image.jpg", f, "image/jpeg")}
        response = requests.post(f"{API_URL}/api/analyze/image", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Detected persons: {result['frame_metrics']['detected_persons']}")
        print(f"Processing time: {result['processing_time_ms']}ms")
    else:
        print(f"Error: {response.text}")
    
    # Clean up
    Path("test_image.jpg").unlink()

def test_with_webcam_image():
    """Test with an image from webcam"""
    print("\nTesting with webcam capture...")
    
    # Capture from webcam
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # Save frame
        cv2.imwrite("webcam_test.jpg", frame)
        
        # Upload to API
        with open("webcam_test.jpg", "rb") as f:
            files = {"file": ("webcam_test.jpg", f, "image/jpeg")}
            response = requests.post(f"{API_URL}/api/analyze/image", files=files)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response preview: {json.dumps(result, indent=2)[:500]}...")
            
            # Save full response
            with open("api_response.json", "w") as f:
                json.dump(result, f, indent=2)
            print("Full response saved to api_response.json")
        else:
            print(f"Error: {response.text}")
        
        # Clean up
        Path("webcam_test.jpg").unlink()
    else:
        print("Failed to capture from webcam")

def test_angle_definitions():
    """Test angle definitions endpoint"""
    print("\nTesting angle definitions...")
    response = requests.get(f"{API_URL}/api/angles/definitions")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Joint angles: {len(result['joint_angles'])}")
        print(f"Segment angles: {len(result['segment_angles'])}")
        print(f"Example joint angle: {result['joint_angles'][0]}")

if __name__ == "__main__":
    print("Starting API tests...\n")
    
    # Test endpoints
    test_health()
    test_angle_definitions()
    test_image_analysis()
    
    # Optional: test with webcam
    try:
        test_with_webcam_image()
    except Exception as e:
        print(f"Webcam test failed: {e}")
    
    print("\nTests completed!")