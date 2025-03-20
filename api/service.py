# rom/service.py
import cv2
import numpy as np
import base64
import logging
from typing import Dict, Tuple, Optional, Union, Any
from utils.pose_detector import PoseDetector
from utils.visualization import PoseVisualizer
from rom.lower_back_test import LowerBackFlexionTest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rom_service")

class ROMService:
    def __init__(self):
        logger.info("Initializing ROM Service with Holistic model")
        try:
            # Initialize Holistic pose detector with higher model complexity
            self.pose_detector = PoseDetector(
                model_complexity=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                enable_segmentation=False
            )
            self.visualizer = PoseVisualizer()
            self.test_types = {
                'lowerback': LowerBackFlexionTest(self.pose_detector, self.visualizer),
                'lowerback_flexion': LowerBackFlexionTest(self.pose_detector, self.visualizer)
                # Add other test types here as needed
            }
            logger.info(f"Loaded test types: {list(self.test_types.keys())}")
        except Exception as e:
            logger.error(f"Error initializing ROM Service: {str(e)}")
            raise
    
    def process_frame(self, frame_data: str, test_type: str) -> Tuple[Dict[str, Any], str]:
        """
        Process a single frame for ROM analysis
        
        Args:
            frame_data: Base64 encoded image data
            test_type: Type of ROM test to perform
            
        Returns:
            Tuple containing ROM data dictionary and processed frame as base64 string
        """
        try:
            # Decode base64 image
            if "base64," in frame_data:
                # Handle data URLs (e.g., from HTML canvas)
                frame_data = frame_data.split('base64,')[1]
                
            nparr = np.frombuffer(base64.b64decode(frame_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None or frame.size == 0:
                logger.error("Invalid frame data received")
                return {"error": "Invalid frame data", "status": "error"}, ""
                
            # Get appropriate test
            test = self.test_types.get(test_type.lower())
            if not test:
                available_tests = list(self.test_types.keys())
                logger.warning(f"Unsupported test type: {test_type}. Available tests: {available_tests}")
                return {
                    "error": f"Unsupported test type: {test_type}", 
                    "available_tests": available_tests,
                    "status": "error"
                }, ""
                
            # Process frame
            processed_frame, rom_data = test.process_frame(frame)
            
            # Encode processed frame
            _, buffer = cv2.imencode('.jpg', processed_frame)
            processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Ensure ROM data has a status field
            if "status" not in rom_data:
                rom_data["status"] = "success"
                
            return rom_data, processed_image_base64
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            # Return minimal ROM data
            return {
                "test": test_type,
                "error": f"Processing error: {str(e)}",
                "status": "error",
                "ROM": [0, 0],
                "rom_range": 0,
                "trunk_angle": 0,
                "is_ready": False
            }, ""
    
    def get_available_tests(self) -> list:
        """Return list of available ROM test types"""
        return list(self.test_types.keys())
        
    def process_full_body_frame(self, frame_data: str) -> Tuple[Dict[str, Any], str]:
        """
        Process a frame with the full Holistic model (face, hands, and body)
        
        Args:
            frame_data: Base64 encoded image data
            
        Returns:
            Dictionary with holistic data and processed frame as base64 string
        """
        try:
            # Decode base64 image
            if "base64," in frame_data:
                frame_data = frame_data.split('base64,')[1]
                
            nparr = np.frombuffer(base64.b64decode(frame_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None or frame.size == 0:
                logger.error("Invalid frame data received")
                return {"error": "Invalid frame data"}, ""
            
            # Get holistic results
            holistic_results = self.pose_detector.get_full_body_results(frame)
            
            # Encode processed frame
            _, buffer = cv2.imencode('.jpg', holistic_results['annotated_frame'])
            processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Extract pose angles if available
            pose_data = {}
            if 'pose_coordinates' in holistic_results and holistic_results['pose_coordinates']:
                coords = holistic_results['pose_coordinates']
                
                # Check for key landmarks
                if all(idx in coords for idx in [11, 23, 25]):  # shoulder, hip, knee
                    shoulder = coords[11][:3]  # x, y, z only
                    hip = coords[23][:3]
                    knee = coords[25][:3]
                    
                    # Calculate angles
                    from utils.angle_calculator import calculate_angle
                    trunk_angle = calculate_angle(shoulder, hip, knee)
                    pose_data['trunk_angle'] = round(trunk_angle, 1)
            
            return {
                'pose_data': pose_data,
                'landmark_count': len(holistic_results.get('pose_coordinates', {})),
                'face_detected': holistic_results.get('face_landmarks') is not None,
                'left_hand_detected': holistic_results.get('left_hand_landmarks') is not None,
                'right_hand_detected': holistic_results.get('right_hand_landmarks') is not None,
                'status': 'success'
            }, processed_image_base64
            
        except Exception as e:
            logger.error(f"Error processing holistic frame: {str(e)}")
            return {"error": f"Processing error: {str(e)}", "status": "error"}, ""