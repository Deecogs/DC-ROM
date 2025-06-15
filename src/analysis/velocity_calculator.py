import numpy as np
from typing import Dict, Optional

class VelocityCalculator:
    """Calculate velocity and movement metrics"""
    
    def calculate_velocity(self, current_person: Dict, previous_frame_data: Dict, 
                         time_delta: float) -> Dict[str, float]:
        """
        Calculate velocity for a person between frames
        
        Args:
            current_person: Current frame person data
            previous_frame_data: Previous frame data
            time_delta: Time between frames in seconds
            
        Returns:
            Velocity in x and y directions (pixels/second)
        """
        # Find matching person in previous frame
        previous_person = None
        for person in previous_frame_data.get('persons', []):
            if person['person_id'] == current_person.get('person_id'):
                previous_person = person
                break
        
        if not previous_person:
            return {'x': 0.0, 'y': 0.0}
        
        # Calculate center of mass movement
        current_center = self._calculate_center_of_mass(current_person['keypoints'])
        
        # Handle the case where previous person data might have different structure
        if 'keypoints' in previous_person:
            previous_keypoints = previous_person['keypoints']
        else:
            # If structure is different, return zero velocity
            return {'x': 0.0, 'y': 0.0}
        
        previous_center = self._calculate_center_of_mass(previous_keypoints)
        
        if current_center and previous_center and time_delta > 0:
            velocity_x = (current_center[0] - previous_center[0]) / time_delta
            velocity_y = (current_center[1] - previous_center[1]) / time_delta
            
            return {
                'x': round(velocity_x, 2),
                'y': round(velocity_y, 2)
            }
        
        return {'x': 0.0, 'y': 0.0}
    
    def _calculate_center_of_mass(self, keypoints: Dict) -> Optional[tuple]:
        """Calculate center of mass from keypoints"""
        # Use hip center if available
        if 'hip_center' in keypoints:
            return (keypoints['hip_center']['x'], keypoints['hip_center']['y'])
        
        # Otherwise use average of hips and shoulders
        key_points = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder']
        valid_points = []
        
        for kp_name in key_points:
            if kp_name in keypoints and keypoints[kp_name]['confidence'] > 0.3:
                valid_points.append([keypoints[kp_name]['x'], keypoints[kp_name]['y']])
        
        if valid_points:
            center = np.mean(valid_points, axis=0)
            return tuple(center)
        
        return None