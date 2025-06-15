import numpy as np
from typing import Dict, List, Tuple, Optional
import cv2

from src.models.model_factory import ModelFactory
from src.config.settings import get_settings

class PoseDetector:
    """Main pose detection class"""
    
    def __init__(self, model_name: str = None):
        self.settings = get_settings()
        model_name = model_name or self.settings.POSE_MODEL
        
        model_config = {
            'min_detection_confidence': self.settings.MIN_DETECTION_CONFIDENCE,
            'min_tracking_confidence': self.settings.MIN_TRACKING_CONFIDENCE,
        }
        
        self.model = ModelFactory.create_model(model_name, model_config)
        self.keypoint_names = self.model.get_keypoint_names()
    
    def detect(self, image: np.ndarray) -> Dict:
        """
        Detect poses in image
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary containing detected poses and metadata
        """
        # Get pose detections
        keypoints_list, scores = self.model.detect_poses(image)
        
        # Filter by confidence thresholds
        filtered_persons = []
        for person_keypoints, person_score in zip(keypoints_list, scores):
            if self._validate_person(person_keypoints, person_score):
                filtered_persons.append({
                    'keypoints': person_keypoints,
                    'score': person_score
                })
        
        return {
            'persons': filtered_persons,
            'num_persons': len(filtered_persons),
            'keypoint_names': self.keypoint_names,
            'image_shape': image.shape[:2]
        }
    
    def _validate_person(self, keypoints: Dict, score: float) -> bool:
        """Validate if person detection meets quality thresholds"""
        # Count valid keypoints
        valid_keypoints = 0
        total_confidence = 0
        
        for kp in keypoints.values():
            if kp['confidence'] >= self.settings.KEYPOINT_LIKELIHOOD_THRESHOLD:
                valid_keypoints += 1
                total_confidence += kp['confidence']
        
        # Check minimum keypoint count
        keypoint_ratio = valid_keypoints / len(keypoints)
        if keypoint_ratio < self.settings.KEYPOINT_NUMBER_THRESHOLD:
            return False
        
        # Check average confidence
        avg_confidence = total_confidence / valid_keypoints if valid_keypoints > 0 else 0
        if avg_confidence < self.settings.AVERAGE_LIKELIHOOD_THRESHOLD:
            return False
        
        return True
    
    def process_video(self, video_path: str, start_time: float = 0, end_time: float = None) -> List[Dict]:
        """Process entire video file"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Set start position
        if start_time > 0:
            cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        
        results = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = frame_count / fps
            if end_time and current_time > end_time:
                break
            
            # Detect poses
            detection_result = self.detect(frame)
            detection_result['frame_id'] = frame_count
            detection_result['timestamp'] = current_time
            
            results.append(detection_result)
            frame_count += 1
        
        cap.release()
        return results