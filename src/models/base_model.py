from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import numpy as np

class BasePoseModel(ABC):
    """Abstract base class for pose estimation models"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.initialize()
    
    @abstractmethod
    def initialize(self):
        """Initialize the model"""
        pass
    
    @abstractmethod
    def detect_poses(self, image: np.ndarray) -> Tuple[List[Dict], List[float]]:
        """
        Detect poses in image
        
        Returns:
            keypoints: List of keypoint dictionaries for each person
            scores: List of confidence scores for each person
        """
        pass
    
    @abstractmethod
    def get_keypoint_names(self) -> List[str]:
        """Get list of keypoint names"""
        pass
    
    @abstractmethod
    def get_connections(self) -> List[Tuple[int, int]]:
        """Get skeleton connections for visualization"""
        pass
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame and return structured data"""
        keypoints, scores = self.detect_poses(frame)
        
        return {
            'keypoints': keypoints,
            'scores': scores,
            'keypoint_names': self.get_keypoint_names(),
            'connections': self.get_connections()
        }   