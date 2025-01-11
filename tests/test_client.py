# test_client.py
import requests
import cv2
import base64
import numpy as np
from pathlib import Path

class ROMCalculatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def encode_frame(self, frame):
        """Encode OpenCV frame to base64."""
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
        
    def decode_frame(self, base64_string):
        """Decode base64 string to OpenCV frame."""
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
    def process_frame(self, frame, test_type='hawkins'):
        """Process a single frame."""
        encoded_frame = self.encode_frame(frame)
        
        response = requests.post(
            f"{self.base_url}/api/v1/process-frame/",
            json={
                'image_data': encoded_frame,
                'test_type': test_type
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['processed_image']:
                result['processed_frame'] = self.decode_frame(result['processed_image'])
            return result
        else:
            raise Exception(f"Error processing frame: {response.text}")
            
    def get_available_tests(self):
        """Get list of available ROM tests."""
        response = requests.get(f"{self.base_url}/api/v1/available-tests/")
        return response.json()
        
    def configure_test(self, test_type, include_visualization=True, save_results=False):
        """Configure ROM test settings."""
        response = requests.post(
            f"{self.base_url}/api/v1/configure-test/",
            json={
                'test_type': test_type,
                'include_visualization': include_visualization,
                'save_results': save_results
            }
        )
        return response.json()