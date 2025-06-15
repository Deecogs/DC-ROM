import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class PersonTracker:
    """Track persons across frames to maintain consistent IDs"""
    
    def __init__(self, max_distance_threshold: float = 100.0):
        self.max_distance_threshold = max_distance_threshold
        self.person_tracks = {}
        self.next_person_id = 0
        self.frame_count = 0
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of person detections with keypoints
            
        Returns:
            List of detections with assigned person IDs
        """
        self.frame_count += 1
        
        if not detections:
            # Mark all tracks as lost
            for track_id in list(self.person_tracks.keys()):
                self.person_tracks[track_id]['frames_lost'] += 1
                if self.person_tracks[track_id]['frames_lost'] > 30:
                    del self.person_tracks[track_id]
            return []
        
        # Calculate centers for all detections
        detection_centers = []
        for det in detections:
            center = self._calculate_center(det['keypoints'])
            detection_centers.append(center)
        
        # Match detections to existing tracks
        matched_detections = []
        used_detections = set()
        used_tracks = set()
        
        # Find best matches
        for track_id, track in self.person_tracks.items():
            best_match_idx = -1
            best_distance = float('inf')
            
            for det_idx, det_center in enumerate(detection_centers):
                if det_idx in used_detections:
                    continue
                
                distance = np.linalg.norm(
                    np.array(track['last_center']) - np.array(det_center)
                )
                
                if distance < best_distance and distance < self.max_distance_threshold:
                    best_distance = distance
                    best_match_idx = det_idx
            
            if best_match_idx >= 0:
                # Update track
                matched_det = detections[best_match_idx].copy()
                matched_det['person_id'] = track_id
                matched_det['tracking_confidence'] = 1.0 - (best_distance / self.max_distance_threshold)
                matched_detections.append(matched_det)
                
                # Update track info
                self.person_tracks[track_id]['last_center'] = detection_centers[best_match_idx]
                self.person_tracks[track_id]['frames_lost'] = 0
                self.person_tracks[track_id]['last_frame'] = self.frame_count
                
                used_detections.add(best_match_idx)
                used_tracks.add(track_id)
        
        # Create new tracks for unmatched detections
        for det_idx, det in enumerate(detections):
            if det_idx not in used_detections:
                new_track_id = self.next_person_id
                self.next_person_id += 1
                
                matched_det = det.copy()
                matched_det['person_id'] = new_track_id
                matched_det['tracking_confidence'] = 0.5  # New track
                matched_detections.append(matched_det)
                
                # Create new track
                self.person_tracks[new_track_id] = {
                    'last_center': detection_centers[det_idx],
                    'frames_lost': 0,
                    'last_frame': self.frame_count,
                    'created_frame': self.frame_count
                }
        
        # Clean up lost tracks
        for track_id in list(self.person_tracks.keys()):
            if track_id not in used_tracks:
                self.person_tracks[track_id]['frames_lost'] += 1
                if self.person_tracks[track_id]['frames_lost'] > 30:
                    del self.person_tracks[track_id]
        
        return matched_detections
    
    def _calculate_center(self, keypoints: Dict) -> Tuple[float, float]:
        """Calculate center of person from keypoints"""
        valid_points = []
        
        # Use hip center if available
        if 'hip_center' in keypoints:
            return (keypoints['hip_center']['x'], keypoints['hip_center']['y'])
        
        # Otherwise use average of all valid keypoints
        for kp in keypoints.values():
            if kp['confidence'] > 0.3:
                valid_points.append([kp['x'], kp['y']])
        
        if valid_points:
            center = np.mean(valid_points, axis=0)
            return tuple(center)
        
        return (0, 0)
    
    def reset(self):
        """Reset tracker state"""
        self.person_tracks = {}
        self.next_person_id = 0
        self.frame_count = 0