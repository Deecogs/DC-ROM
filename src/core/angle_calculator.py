import numpy as np
from typing import Dict, List, Optional

from src.utils.angle_definitions import (
    JOINT_ANGLES, 
    SEGMENT_ANGLES, 
    calculate_angle_2d,
    calculate_ankle_angle
)
from src.utils.skeleton_definitions import KEYPOINT_MAP

class AngleCalculator:
    """Calculate joint and segment angles from keypoints"""
    
    def __init__(self, flip_left_right: bool = True):
        self.flip_left_right = flip_left_right
        self.joint_angle_defs = JOINT_ANGLES
        self.segment_angle_defs = SEGMENT_ANGLES
    
    def calculate_angles(self, keypoints: Dict) -> Dict:
        """
        Calculate all angles for a person
        
        Args:
            keypoints: Dictionary of keypoint positions
            
        Returns:
            Dictionary containing joint and segment angles
        """
        # Detect facing direction if flip_left_right is enabled
        if self.flip_left_right:
            keypoints = self._adjust_for_direction(keypoints)
        
        joint_angles = self._calculate_joint_angles(keypoints)
        segment_angles = self._calculate_segment_angles(keypoints)
        
        return {
            'joint_angles': joint_angles,
            'segment_angles': segment_angles
        }
    
    def _adjust_for_direction(self, keypoints: Dict) -> Dict:
        """Adjust keypoints based on facing direction"""
        # Detect direction based on toe-heel orientation
        try:
            left_orientation = keypoints['left_toe']['x'] - keypoints['left_heel']['x']
            right_orientation = keypoints['right_toe']['x'] - keypoints['right_heel']['x']
            
            # Create a copy to avoid modifying original
            adjusted_keypoints = {}
            for name, kp in keypoints.items():
                adjusted_keypoints[name] = kp.copy()
            
            # Flip x-coordinates if facing left
            if left_orientation < 0:
                for name in adjusted_keypoints:
                    if name.startswith('left_'):
                        adjusted_keypoints[name]['x'] *= -1
            
            if right_orientation < 0:
                for name in adjusted_keypoints:
                    if name.startswith('right_'):
                        adjusted_keypoints[name]['x'] *= -1
                        
            return adjusted_keypoints
        except:
            return keypoints
    
    def _calculate_joint_angles(self, keypoints: Dict) -> Dict:
        """Calculate all joint angles"""
        angles = {}
        
        for angle_name, angle_def in self.joint_angle_defs.items():
            try:
                # Map point names to keypoints
                points = []
                for point_name in angle_def['points']:
                    if point_name in keypoints:
                        points.append(keypoints[point_name])
                    elif point_name in KEYPOINT_MAP and KEYPOINT_MAP[point_name] in keypoints:
                        points.append(keypoints[KEYPOINT_MAP[point_name]])
                    else:
                        points.append(None)
                
                # Check if all required points are available
                if any(p is None for p in points[:3]):  # Need at least 3 points
                    angles[angle_name] = None
                    continue
                
                # Special case for ankle angle
                if angle_def['type'] == 'dorsiflexion':
                    if len(points) >= 4 and points[3] is not None:
                        angle = calculate_ankle_angle(points[0], points[1], points[2], points[3])
                    else:
                        angle = calculate_angle_2d(points[0], points[1], points[2])
                else:
                    angle = calculate_angle_2d(points[0], points[1], points[2])
                
                # Apply offset and scale
                if not np.isnan(angle):
                    angle = (angle + angle_def['offset']) * angle_def['scale']
                    angles[angle_name] = round(angle, 1)
                else:
                    angles[angle_name] = None
                    
            except Exception as e:
                angles[angle_name] = None
        
        return angles
    
    def _calculate_segment_angles(self, keypoints: Dict) -> Dict:
        """Calculate all segment angles"""
        angles = {}
        
        for angle_name, angle_def in self.segment_angle_defs.items():
            try:
                # Map point names to keypoints
                points = []
                for point_name in angle_def['points']:
                    if point_name in keypoints:
                        points.append(keypoints[point_name])
                    elif point_name in KEYPOINT_MAP and KEYPOINT_MAP[point_name] in keypoints:
                        points.append(keypoints[KEYPOINT_MAP[point_name]])
                    else:
                        points.append(None)
                
                # Check if all required points are available
                if any(p is None for p in points):
                    angles[angle_name] = None
                    continue
                
                # Calculate angle with horizontal
                angle = calculate_angle_2d(points[0], points[1])
                
                # Apply offset and scale
                if not np.isnan(angle):
                    angle = (angle + angle_def['offset']) * angle_def['scale']
                    angles[angle_name] = round(angle, 1)
                else:
                    angles[angle_name] = None
                    
            except Exception as e:
                angles[angle_name] = None
        
        return angles