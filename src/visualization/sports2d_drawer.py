"""
Sports2D-style visualization for pose and angles
Matches the exact drawing style from Sports2D
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional

class Sports2DVisualizer:
    """Visualizer that matches Sports2D drawing style"""
    
    def __init__(self):
        self.colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), 
                      (0, 255, 255), (0, 0, 0), (255, 255, 255)]
        self.thickness = 2
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_thickness = 1
        
    def draw_frame(self, img: np.ndarray, result: Dict, display_angle_values_on: List[str] = ['body', 'list']) -> np.ndarray:
        """
        Main drawing function that matches Sports2D style
        
        Args:
            img: Input image
            result: API result dictionary
            display_angle_values_on: Where to display angles ['body', 'list', 'none']
        """
        # Draw pose and angles for each person
        for person_idx, person in enumerate(result['persons']):
            color = self.colors[person_idx % len(self.colors)]
            
            # Draw skeleton
            self._draw_skeleton(img, person['keypoints'], color)
            
            # Draw keypoints
            self._draw_keypoints(img, person['keypoints'], person.get('tracking_confidence', 1.0))
            
            # Draw bounding box with person ID
            self._draw_bounding_box(img, person['keypoints'], person['person_id'], color)
            
            # Draw angles
            if 'body' in display_angle_values_on or 'list' in display_angle_values_on:
                self._draw_all_angles(img, person, person_idx, display_angle_values_on, color)
        
        return img
    
    def _draw_skeleton(self, img: np.ndarray, keypoints: Dict, color: Tuple):
        """Draw skeleton connections"""
        connections = [
            # Face
            ('left_ear', 'left_eye'), ('right_ear', 'right_eye'),
            ('left_eye', 'nose'), ('right_eye', 'nose'),
            
            # Arms
            ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist'),
            
            # Torso
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_hip'), ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            
            # Legs
            ('left_hip', 'left_knee'), ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'), ('right_knee', 'right_ankle'),
            
            # Feet
            ('left_ankle', 'left_heel'), ('left_ankle', 'left_foot_index'),
            ('left_heel', 'left_foot_index'),
            ('right_ankle', 'right_heel'), ('right_ankle', 'right_foot_index'),
            ('right_heel', 'right_foot_index'),
            
            # Center connections
            ('neck', 'hip_center')
        ]
        
        for start, end in connections:
            if start in keypoints and end in keypoints:
                if keypoints[start]['confidence'] > 0.3 and keypoints[end]['confidence'] > 0.3:
                    pt1 = (int(keypoints[start]['x']), int(keypoints[start]['y']))
                    pt2 = (int(keypoints[end]['x']), int(keypoints[end]['y']))
                    cv2.line(img, pt1, pt2, color, self.thickness)
    
    def _draw_keypoints(self, img: np.ndarray, keypoints: Dict, confidence: float = None):
        """Draw keypoints with confidence-based coloring"""
        import matplotlib.cm as cm
        cmap = cm.get_cmap('RdYlGn')
        
        for kp_name, kp in keypoints.items():
            if kp['confidence'] > 0.3:
                # Color based on confidence
                color_rgb = cmap(kp['confidence'])
                color_bgr = (int(color_rgb[2]*255), int(color_rgb[1]*255), int(color_rgb[0]*255))
                
                center = (int(kp['x']), int(kp['y']))
                cv2.circle(img, center, 5, color_bgr, -1)
                cv2.circle(img, center, 6, (255, 255, 255), 1)
    
    def _draw_bounding_box(self, img: np.ndarray, keypoints: Dict, person_id: int, color: Tuple):
        """Draw bounding box around person"""
        valid_points = [(kp['x'], kp['y']) for kp in keypoints.values() if kp['confidence'] > 0.3]
        
        if valid_points:
            points = np.array(valid_points)
            x_min, y_min = np.min(points, axis=0).astype(int)
            x_max, y_max = np.max(points, axis=0).astype(int)
            
            # Add padding
            padding = 20
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(img.shape[1], x_max + padding)
            y_max = min(img.shape[0], y_max + padding)
            
            # Draw box
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, 2)
            
            # Draw person ID
            label = f"Person {person_id}"
            label_size, _ = cv2.getTextSize(label, self.font, self.font_scale + 0.2, self.font_thickness + 1)
            cv2.rectangle(img, (x_min, y_min - label_size[1] - 10), 
                         (x_min + label_size[0] + 10, y_min), color, -1)
            cv2.putText(img, label, (x_min + 5, y_min - 5), self.font, 
                       self.font_scale + 0.2, (255, 255, 255), self.font_thickness + 1)
    
    def _draw_all_angles(self, img: np.ndarray, person: Dict, person_idx: int, 
                        display_angle_values_on: List[str], color: Tuple):
        """Draw all angles in Sports2D style"""
        keypoints = person['keypoints']
        angles = person['angles']
        
        # Starting position for angle list
        if 'list' in display_angle_values_on:
            y_offset = 70 + person_idx * 350
            x_offset = 10
            
            # Person label
            cv2.putText(img, f"Person {person['person_id']}", 
                       (x_offset, y_offset), self.font, 
                       self.font_scale + 0.3, color, self.font_thickness + 1)
            y_offset += 30
        
        # Draw joint angles
        joint_angles = angles['joint_angles']
        angle_line = 0
        
        for angle_name, angle_value in joint_angles.items():
            if angle_value is not None:
                # Draw on body
                if 'body' in display_angle_values_on:
                    self._draw_joint_angle_on_body(img, angle_name, angle_value, keypoints, color)
                
                # Draw in list
                if 'list' in display_angle_values_on:
                    y_pos = y_offset + angle_line * 25
                    self._draw_angle_in_list(img, angle_name, angle_value, x_offset, y_pos, (0, 255, 0))
                    angle_line += 1
        
        # Draw segment angles
        if 'list' in display_angle_values_on:
            y_offset += (angle_line + 1) * 25
            cv2.putText(img, "Segment Angles:", (x_offset, y_offset), self.font, 
                       self.font_scale, (255, 255, 255), self.font_thickness)
            y_offset += 25
            angle_line = 0
        
        segment_angles = angles['segment_angles']
        for angle_name, angle_value in segment_angles.items():
            if angle_value is not None:
                # Draw on body
                if 'body' in display_angle_values_on:
                    self._draw_segment_angle_on_body(img, angle_name, angle_value, keypoints, color)
                
                # Draw in list
                if 'list' in display_angle_values_on:
                    y_pos = y_offset + angle_line * 25
                    self._draw_angle_in_list(img, angle_name, angle_value, x_offset, y_pos, (255, 255, 255))
                    angle_line += 1
    
    def _draw_joint_angle_on_body(self, img: np.ndarray, angle_name: str, angle_value: float, 
                                  keypoints: Dict, color: Tuple):
        """Draw joint angle visualization on body (Sports2D style)"""
        # Joint angle keypoint mappings
        joint_mappings = {
            'right_ankle': ('right_knee', 'right_ankle', 'right_foot_index', 'right_heel'),
            'left_ankle': ('left_knee', 'left_ankle', 'left_foot_index', 'left_heel'),
            'right_knee': ('right_hip', 'right_knee', 'right_ankle'),
            'left_knee': ('left_hip', 'left_knee', 'left_ankle'),
            'right_hip': ('right_knee', 'right_hip', 'neck'),
            'left_hip': ('left_knee', 'left_hip', 'neck'),
            'right_shoulder': ('right_elbow', 'right_shoulder', 'neck'),
            'left_shoulder': ('left_elbow', 'left_shoulder', 'neck'),
            'right_elbow': ('right_shoulder', 'right_elbow', 'right_wrist'),
            'left_elbow': ('left_shoulder', 'left_elbow', 'left_wrist')
        }
        
        if angle_name in joint_mappings:
            points = joint_mappings[angle_name]
            if all(p in keypoints for p in points[:3]) and all(keypoints[p]['confidence'] > 0.3 for p in points[:3]):
                # Get the middle point (joint location)
                joint_pt = (int(keypoints[points[1]]['x']), int(keypoints[points[1]]['y']))
                
                # Calculate vectors for angle arc
                pt1 = np.array([keypoints[points[0]]['x'], keypoints[points[0]]['y']])
                pt2 = np.array([keypoints[points[2]]['x'], keypoints[points[2]]['y']])
                
                v1 = pt1 - joint_pt
                v2 = pt2 - joint_pt
                
                # Draw angle arc
                radius = 40
                if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                    angle1 = np.degrees(np.arctan2(v1[1], v1[0]))
                    angle2 = np.degrees(np.arctan2(v2[1], v2[0]))
                    
                    # Draw arc
                    cv2.ellipse(img, joint_pt, (radius, radius), 0, 
                               min(angle1, angle2), max(angle1, angle2), (0, 255, 0), 2)
                
                # Draw angle value
                text_offset = v1 + v2
                if np.linalg.norm(text_offset) > 0:
                    text_offset = text_offset / np.linalg.norm(text_offset) * (radius + 20)
                    text_pos = (int(joint_pt[0] + text_offset[0]), int(joint_pt[1] + text_offset[1]))
                else:
                    text_pos = (joint_pt[0] + radius, joint_pt[1])
                
                # Background for text
                text = f"{angle_value:.0f}"
                text_size, _ = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)
                cv2.rectangle(img, (text_pos[0] - 2, text_pos[1] - text_size[1] - 2),
                             (text_pos[0] + text_size[0] + 2, text_pos[1] + 2), (0, 0, 0), -1)
                cv2.putText(img, text, text_pos, self.font, self.font_scale, (0, 255, 0), self.font_thickness)
    
    def _draw_segment_angle_on_body(self, img: np.ndarray, angle_name: str, angle_value: float,
                                   keypoints: Dict, color: Tuple):
        """Draw segment angle visualization on body"""
        # Segment angle keypoint mappings
        segment_mappings = {
            'right_foot': ('right_foot_index', 'right_heel'),
            'left_foot': ('left_foot_index', 'left_heel'),
            'right_shank': ('right_knee', 'right_ankle'),
            'left_shank': ('left_knee', 'left_ankle'),
            'right_thigh': ('right_hip', 'right_knee'),
            'left_thigh': ('left_hip', 'left_knee'),
            'trunk': ('hip_center', 'neck'),
            'right_arm': ('right_shoulder', 'right_elbow'),
            'left_arm': ('left_shoulder', 'left_elbow'),
            'right_forearm': ('right_elbow', 'right_wrist'),
            'left_forearm': ('left_elbow', 'left_wrist')
        }
        
        if angle_name in segment_mappings:
            points = segment_mappings[angle_name]
            if all(p in keypoints for p in points) and all(keypoints[p]['confidence'] > 0.3 for p in points):
                # Get midpoint of segment
                pt1 = np.array([keypoints[points[0]]['x'], keypoints[points[0]]['y']])
                pt2 = np.array([keypoints[points[1]]['x'], keypoints[points[1]]['y']])
                midpoint = ((pt1 + pt2) / 2).astype(int)
                
                # Draw horizontal reference line
                cv2.line(img, (midpoint[0] - 20, midpoint[1]), 
                        (midpoint[0] + 20, midpoint[1]), (255, 255, 255), 1)
                
                # Draw segment direction line
                direction = pt1 - pt2
                if np.linalg.norm(direction) > 0:
                    direction = direction / np.linalg.norm(direction) * 20
                    cv2.line(img, tuple(midpoint), 
                            tuple((midpoint + direction).astype(int)), (255, 255, 255), 2)
                
                # Draw angle value
                text_pos = (midpoint[0] + 25, midpoint[1])
                text = f"{angle_value:.0f}"
                cv2.putText(img, text, text_pos, self.font, self.font_scale, (255, 255, 255), self.font_thickness)
    
    def _draw_angle_in_list(self, img: np.ndarray, angle_name: str, angle_value: float,
                           x_offset: int, y_offset: int, color: Tuple):
        """Draw angle in list with progress bar (Sports2D style)"""
        # Draw angle name
        cv2.putText(img, f"{angle_name}:", (x_offset + 20, y_offset), 
                   self.font, self.font_scale, (200, 200, 200), self.font_thickness)
        
        # Draw angle value
        value_x = x_offset + 180
        cv2.putText(img, f"{angle_value:.1f}°", (value_x, y_offset), 
                   self.font, self.font_scale, color, self.font_thickness)
        
        # Draw progress bar
        bar_x = x_offset + 250
        bar_y = y_offset - 8
        bar_width = 100
        bar_height = 10
        
        # Background
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     (50, 50, 50), -1)
        
        # Progress fill
        if 'ankle' in angle_name or 'knee' in angle_name or 'hip' in angle_name:
            # Joint angles: 0-180 degrees
            fill_percent = min(angle_value / 180, 1.0)
        else:
            # Segment angles: normalize from -90 to 90
            fill_percent = (angle_value + 90) / 180
        
        fill_width = int(fill_percent * bar_width)
        fill_width = max(0, min(fill_width, bar_width))
        
        if fill_width > 0:
            cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                         color, -1)