import numpy as np
from typing import Dict, Tuple

class MetricsCalculator:
    """Calculate various metrics from pose data"""
    
    def calculate_person_metrics(self, keypoints: Dict, image_shape: Tuple[int, int]) -> Dict:
        """
        Calculate metrics for a person
        
        Args:
            keypoints: Dictionary of keypoint positions
            image_shape: (height, width) of the image
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        # Calculate height in pixels
        metrics['height_pixels'] = self._calculate_height(keypoints)
        
        # Calculate center of mass
        center = self._calculate_center_of_mass(keypoints)
        metrics['center_of_mass'] = {
            'x': round(center[0], 2),
            'y': round(center[1], 2)
        } if center else {'x': 0, 'y': 0}
        
        # Determine visible side
        metrics['visible_side'] = self._determine_visible_side(keypoints)
        
        # Determine movement direction
        metrics['movement_direction'] = self._determine_movement_direction(keypoints)
        
        return metrics
    
    def _calculate_height(self, keypoints: Dict) -> float:
        """Calculate person height in pixels"""
        # Find topmost and bottommost valid keypoints
        top_y = float('inf')
        bottom_y = float('-inf')
        
        # Priority keypoints for height calculation
        top_keypoints = ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear']
        bottom_keypoints = ['left_ankle', 'right_ankle', 'left_heel', 'right_heel', 
                           'left_toe', 'right_toe']
        
        # Find top point
        for kp_name in top_keypoints:
            if kp_name in keypoints and keypoints[kp_name]['confidence'] > 0.3:
                top_y = min(top_y, keypoints[kp_name]['y'])
        
        # Find bottom point
        for kp_name in bottom_keypoints:
            if kp_name in keypoints and keypoints[kp_name]['confidence'] > 0.3:
                bottom_y = max(bottom_y, keypoints[kp_name]['y'])
        
        # If specific keypoints not found, use all keypoints
        if top_y == float('inf') or bottom_y == float('-inf'):
            valid_y_coords = [kp['y'] for kp in keypoints.values() 
                            if kp['confidence'] > 0.3]
            if valid_y_coords:
                top_y = min(valid_y_coords)
                bottom_y = max(valid_y_coords)
            else:
                return 0
        
        height = bottom_y - top_y
        return round(max(0, height), 2)
    
    def _calculate_center_of_mass(self, keypoints: Dict) -> Tuple[float, float]:
        """Calculate center of mass from keypoints"""
        # Use hip center if available
        if 'hip_center' in keypoints:
            return (keypoints['hip_center']['x'], keypoints['hip_center']['y'])
        
        # Otherwise use weighted average of key body parts
        weighted_points = {
            'left_hip': 0.15,
            'right_hip': 0.15,
            'left_shoulder': 0.1,
            'right_shoulder': 0.1,
            'neck': 0.2,
            'left_knee': 0.075,
            'right_knee': 0.075,
            'left_ankle': 0.075,
            'right_ankle': 0.075
        }
        
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for kp_name, weight in weighted_points.items():
            if kp_name in keypoints and keypoints[kp_name]['confidence'] > 0.3:
                weighted_x += keypoints[kp_name]['x'] * weight
                weighted_y += keypoints[kp_name]['y'] * weight
                total_weight += weight
        
        if total_weight > 0:
            return (weighted_x / total_weight, weighted_y / total_weight)
        
        # Fallback to simple average
        valid_points = [(kp['x'], kp['y']) for kp in keypoints.values() 
                       if kp['confidence'] > 0.3]
        if valid_points:
            center = np.mean(valid_points, axis=0)
            return tuple(center)
        
        return (0, 0)
    
    def _determine_visible_side(self, keypoints: Dict) -> str:
        """Determine which side of the person is visible"""
        # Check foot orientation
        try:
            left_foot_dir = (keypoints.get('left_toe', {}).get('x', 0) - 
                           keypoints.get('left_heel', {}).get('x', 0))
            right_foot_dir = (keypoints.get('right_toe', {}).get('x', 0) - 
                            keypoints.get('right_heel', {}).get('x', 0))
            
            # Both feet pointing right
            if left_foot_dir > 10 and right_foot_dir > 10:
                return 'right'
            # Both feet pointing left
            elif left_foot_dir < -10 and right_foot_dir < -10:
                return 'left'
            # Mixed or unclear
            else:
                return 'front'
        except:
            return 'unknown'
    
    def _determine_movement_direction(self, keypoints: Dict) -> str:
        """Determine general movement direction based on pose"""
        # This is a simplified version - in full implementation,
        # this would compare with previous frames
        visible_side = self._determine_visible_side(keypoints)
        
        if visible_side == 'right':
            return 'left_to_right'
        elif visible_side == 'left':
            return 'right_to_left'
        else:
            return 'stationary'