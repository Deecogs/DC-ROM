import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple
import cv2

from src.models.base_model import BasePoseModel
from src.utils.skeleton_definitions import (
    MEDIAPIPE_KEYPOINTS, 
    MEDIAPIPE_CONNECTIONS,
    get_neck_position,
    get_hip_center
)

class MediaPipeModel(BasePoseModel):
    """MediaPipe Holistic model for pose estimation"""
    
    def initialize(self):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=self.config.get('min_detection_confidence', 0.5),
            min_tracking_confidence=self.config.get('min_tracking_confidence', 0.5),
            model_complexity=self.config.get('model_complexity', 1),
            enable_segmentation=False,
            smooth_landmarks=True
        )
        self.keypoint_names = list(MEDIAPIPE_KEYPOINTS.keys()) + ['neck', 'hip_center']
    
    def detect_poses(self, image: np.ndarray) -> Tuple[List[Dict], List[float]]:
        """Detect poses using MediaPipe"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.holistic.process(image_rgb)
        
        if not results.pose_landmarks:
            return [], []
        
        # Extract keypoints
        h, w = image.shape[:2]
        keypoints = {}
        
        # Process pose landmarks
        for name, idx in MEDIAPIPE_KEYPOINTS.items():
            landmark = results.pose_landmarks.landmark[idx]
            keypoints[name] = {
                'x': landmark.x * w,
                'y': landmark.y * h,
                'confidence': landmark.visibility
            }
        
        # Add computed keypoints
        keypoints['neck'] = get_neck_position(keypoints)
        keypoints['hip_center'] = get_hip_center(keypoints)
        
        # MediaPipe only detects one person, so return as single-person list
        return [keypoints], [self._calculate_average_confidence(keypoints)]
    
    def _calculate_average_confidence(self, keypoints: Dict) -> float:
        """Calculate average confidence score"""
        confidences = [kp['confidence'] for kp in keypoints.values() if 'confidence' in kp]
        return np.mean(confidences) if confidences else 0.0
    
    def get_keypoint_names(self) -> List[str]:
        """Get list of keypoint names"""
        return self.keypoint_names
    
    def get_connections(self) -> List[Tuple[int, int]]:
        """Get skeleton connections"""
        return MEDIAPIPE_CONNECTIONS
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'holistic'):
            self.holistic.close()