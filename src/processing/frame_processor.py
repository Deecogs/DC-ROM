import numpy as np
from typing import Dict, List, Optional
import time

from src.core.pose_detector import PoseDetector
from src.core.angle_calculator import AngleCalculator
from src.core.person_tracker import PersonTracker
from src.analysis.velocity_calculator import VelocityCalculator
from src.analysis.metrics import MetricsCalculator

class FrameProcessor:
    """Process frames to extract pose, angles, and metrics"""
    
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.angle_calculator = AngleCalculator()
        self.person_tracker = PersonTracker()
        self.velocity_calculator = VelocityCalculator()
        self.metrics_calculator = MetricsCalculator()
        
        self.previous_frame_data = None
        self.frame_count = 0
        self.fps = 30  # Default FPS, will be updated
    
    def process_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> Dict:
        """
        Process a single frame
        
        Args:
            frame: Input frame (BGR format)
            timestamp: Optional timestamp in seconds
            
        Returns:
            Processed frame data in JSON-serializable format
        """
        start_time = time.time()
        
        # Update timestamp
        if timestamp is None:
            timestamp = self.frame_count / self.fps
        
        # Detect poses
        detection_result = self.pose_detector.detect(frame)
        
        # Track persons
        tracked_persons = self.person_tracker.update(detection_result['persons'])
        
        # Process each person
        processed_persons = []
        for person in tracked_persons:
            # Calculate angles
            angles = self.angle_calculator.calculate_angles(person['keypoints'])
            
            # Calculate metrics
            metrics = self.metrics_calculator.calculate_person_metrics(
                person['keypoints'],
                detection_result['image_shape']
            )
            
            # Calculate velocity if we have previous frame
            if self.previous_frame_data:
                velocity = self.velocity_calculator.calculate_velocity(
                    person,
                    self.previous_frame_data,
                    1.0 / self.fps
                )
                metrics['velocity'] = velocity
            else:
                metrics['velocity'] = {'x': 0.0, 'y': 0.0}
            
            # Build person data
            person_data = {
                'person_id': person['person_id'],
                'tracking_confidence': person['tracking_confidence'],
                'keypoints': self._serialize_keypoints(person['keypoints']),
                'angles': angles,
                'metrics': metrics
            }
            
            processed_persons.append(person_data)
        
        # Calculate frame metrics
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        frame_data = {
            'frame_id': self.frame_count,
            'timestamp': timestamp,
            'processing_time_ms': round(processing_time, 2),
            'persons': processed_persons,
            'frame_metrics': {
                'detected_persons': len(processed_persons),
                'average_confidence': self._calculate_average_confidence(processed_persons),
                'processing_fps': round(1000 / processing_time if processing_time > 0 else 0, 1)
            }
        }
        
        # Update state
        self.previous_frame_data = frame_data
        self.frame_count += 1
        
        return frame_data
    
    def _serialize_keypoints(self, keypoints: Dict) -> Dict:
        """Ensure keypoints are JSON serializable"""
        serialized = {}
        for name, kp in keypoints.items():
            serialized[name] = {
                'x': round(float(kp['x']), 2),
                'y': round(float(kp['y']), 2),
                'confidence': round(float(kp['confidence']), 3)
            }
        return serialized
    
    def _calculate_average_confidence(self, persons: List[Dict]) -> float:
        """Calculate average confidence across all persons"""
        if not persons:
            return 0.0
        
        total_confidence = 0
        count = 0
        
        for person in persons:
            for kp in person['keypoints'].values():
                total_confidence += kp['confidence']
                count += 1
        
        return round(total_confidence / count if count > 0 else 0.0, 3)
    
    def reset(self):
        """Reset processor state"""
        self.person_tracker.reset()
        self.previous_frame_data = None
        self.frame_count = 0
    
    def set_fps(self, fps: float):
        """Set the frames per second for velocity calculations"""
        self.fps = fps