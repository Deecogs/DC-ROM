"""
Debug test for API with timeout and progress tracking
"""

import requests
import time
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def test_with_timeout():
    """Test API with timeout and progress tracking"""
    
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        print(f"   ✓ API is responding (status: {response.status_code})")
    except requests.exceptions.Timeout:
        print("   ✗ API health check timed out")
        return
    except Exception as e:
        print(f"   ✗ Cannot connect to API: {e}")
        return
    
    print("\n2. Creating simple test image...")
    # Create a very simple test image
    import cv2
    import numpy as np
    
    # Small image for faster processing
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    cv2.imwrite("small_test.jpg", img)
    print("   ✓ Created small_test.jpg (200x200)")
    
    print("\n3. Testing image upload with timeout...")
    start_time = time.time()
    
    try:
        with open("small_test.jpg", "rb") as f:
            files = {"file": ("small_test.jpg", f, "image/jpeg")}
            print("   Sending request...")
            response = requests.post(
                f"{API_URL}/api/analyze/image", 
                files=files,
                timeout=30  # 30 second timeout
            )
        
        elapsed = time.time() - start_time
        print(f"   ✓ Response received in {elapsed:.2f} seconds")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Processing time reported by API: {result.get('processing_time_ms', 'N/A')}ms")
            print(f"   Persons detected: {result.get('frame_metrics', {}).get('detected_persons', 0)}")
        
    except requests.exceptions.Timeout:
        print(f"   ✗ Request timed out after 30 seconds")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Clean up
    Path("small_test.jpg").unlink(missing_ok=True)

def test_api_directly():
    """Test the API components directly"""
    print("\n4. Testing API components directly...")
    
    try:
        # Test if we can import and initialize the components
        print("   Testing imports...")
        from src.processing.frame_processor import FrameProcessor
        print("   ✓ FrameProcessor imported")
        
        from src.models.mediapipe_model import MediaPipeModel
        print("   ✓ MediaPipeModel imported")
        
        # Try to create instances
        print("   Creating processor instance...")
        processor = FrameProcessor()
        print("   ✓ FrameProcessor created")
        
        # Test with a simple numpy array
        import numpy as np
        import cv2
        
        print("   Processing a test frame...")
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        start_time = time.time()
        result = processor.process_frame(test_frame)
        elapsed = time.time() - start_time
        
        print(f"   ✓ Frame processed in {elapsed:.2f} seconds")
        print(f"   Result keys: {list(result.keys())}")
        
    except Exception as e:
        print(f"   ✗ Error testing components: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("API Debug Test")
    print("="*60)
    print()
    
    # Run tests
    test_with_timeout()
    
    # Optional: test components directly
    print("\nDo you want to test API components directly? (y/n): ", end="")
    if input().lower() == 'y':
        test_api_directly()
    
    print("\n" + "="*60)