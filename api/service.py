# api/service.py
import cv2
import numpy as np
import base64
from typing import Dict, Tuple
from utils.pose_detector import PoseDetector
from utils.visualization import PoseVisualizer
from rom.hawkins_test import HawkinsTest
# Import other test types here

class ROMService:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.visualizer = PoseVisualizer()
        self.test_types = {
            'hawkins': HawkinsTest(self.pose_detector, self.visualizer)
            # Add other test types here
        }
    
    def process_frame(self, frame_data: str, test_type: str) -> Tuple[Dict, str]:
        # Decode base64 image
        nparr = np.frombuffer(base64.b64decode(frame_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Get appropriate test
        test = self.test_types.get(test_type.lower())
        if not test:
            raise ValueError(f"Unsupported test type: {test_type}")
            
        # Process frame
        processed_frame, rom_data = test.process_frame(frame)
        
        # Encode processed frame
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return rom_data, processed_image_base64