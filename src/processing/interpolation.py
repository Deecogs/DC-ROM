import numpy as np
from typing import List, Dict, Optional

def interpolate_missing_keypoints(
    keypoints_sequence: List[Dict],
    max_gap_size: int = 10
) -> List[Dict]:
    """
    Interpolate missing keypoints in a sequence
    
    Args:
        keypoints_sequence: List of keypoint dictionaries across frames
        max_gap_size: Maximum gap size to interpolate
        
    Returns:
        Interpolated keypoints sequence
    """
    if not keypoints_sequence:
        return keypoints_sequence
    
    # Get all keypoint names
    all_keypoint_names = set()
    for frame_kpts in keypoints_sequence:
        all_keypoint_names.update(frame_kpts.keys())
    
    # Interpolate each keypoint
    for kp_name in all_keypoint_names:
        # Extract time series for this keypoint
        x_values = []
        y_values = []
        confidence_values = []
        valid_indices = []
        
        for i, frame_kpts in enumerate(keypoints_sequence):
            if kp_name in frame_kpts and frame_kpts[kp_name]['confidence'] > 0.3:
                x_values.append(frame_kpts[kp_name]['x'])
                y_values.append(frame_kpts[kp_name]['y'])
                confidence_values.append(frame_kpts[kp_name]['confidence'])
                valid_indices.append(i)
        
        if len(valid_indices) < 2:
            continue
        
        # Interpolate gaps
        for i in range(len(valid_indices) - 1):
            start_idx = valid_indices[i]
            end_idx = valid_indices[i + 1]
            gap_size = end_idx - start_idx - 1
            
            if gap_size > 0 and gap_size <= max_gap_size:
                # Linear interpolation
                x_start = x_values[i]
                x_end = x_values[i + 1]
                y_start = y_values[i]
                y_end = y_values[i + 1]
                conf_start = confidence_values[i]
                conf_end = confidence_values[i + 1]
                
                for j in range(1, gap_size + 1):
                    alpha = j / (gap_size + 1)
                    frame_idx = start_idx + j
                    
                    if kp_name not in keypoints_sequence[frame_idx]:
                        keypoints_sequence[frame_idx][kp_name] = {}
                    
                    keypoints_sequence[frame_idx][kp_name] = {
                        'x': x_start + alpha * (x_end - x_start),
                        'y': y_start + alpha * (y_end - y_start),
                        'confidence': conf_start + alpha * (conf_end - conf_start)
                    }
    
    return keypoints_sequence

def interpolate_angles(
    angles_sequence: List[Dict],
    max_gap_size: int = 10
) -> List[Dict]:
    """
    Interpolate missing angles in a sequence
    
    Args:
        angles_sequence: List of angle dictionaries across frames
        max_gap_size: Maximum gap size to interpolate
        
    Returns:
        Interpolated angles sequence
    """
    if not angles_sequence:
        return angles_sequence
    
    # Get all angle names
    joint_angle_names = set()
    segment_angle_names = set()
    
    for frame_angles in angles_sequence:
        if 'joint_angles' in frame_angles:
            joint_angle_names.update(frame_angles['joint_angles'].keys())
        if 'segment_angles' in frame_angles:
            segment_angle_names.update(frame_angles['segment_angles'].keys())
    
    # Interpolate joint angles
    for angle_name in joint_angle_names:
        values = []
        valid_indices = []
        
        for i, frame_angles in enumerate(angles_sequence):
            if ('joint_angles' in frame_angles and 
                angle_name in frame_angles['joint_angles'] and
                frame_angles['joint_angles'][angle_name] is not None):
                values.append(frame_angles['joint_angles'][angle_name])
                valid_indices.append(i)
        
        # Interpolate gaps
        interpolated_values = _interpolate_1d_gaps(
            values, valid_indices, len(angles_sequence), max_gap_size
        )
        
        # Update sequence
        for i, val in enumerate(interpolated_values):
            if val is not None:
                if 'joint_angles' not in angles_sequence[i]:
                    angles_sequence[i]['joint_angles'] = {}
                angles_sequence[i]['joint_angles'][angle_name] = val
    
    # Similar process for segment angles
    for angle_name in segment_angle_names:
        values = []
        valid_indices = []
        
        for i, frame_angles in enumerate(angles_sequence):
            if ('segment_angles' in frame_angles and 
                angle_name in frame_angles['segment_angles'] and
                frame_angles['segment_angles'][angle_name] is not None):
                values.append(frame_angles['segment_angles'][angle_name])
                valid_indices.append(i)
        
        interpolated_values = _interpolate_1d_gaps(
            values, valid_indices, len(angles_sequence), max_gap_size
        )
        
        for i, val in enumerate(interpolated_values):
            if val is not None:
                if 'segment_angles' not in angles_sequence[i]:
                    angles_sequence[i]['segment_angles'] = {}
                angles_sequence[i]['segment_angles'][angle_name] = val
    
    return angles_sequence

def _interpolate_1d_gaps(
    values: List[float],
    valid_indices: List[int],
    total_length: int,
    max_gap_size: int
) -> List[Optional[float]]:
    """Helper function to interpolate 1D data gaps"""
    result = [None] * total_length
    
    # Fill in known values
    for val, idx in zip(values, valid_indices):
        result[idx] = val
    
    # Interpolate gaps
    for i in range(len(valid_indices) - 1):
        start_idx = valid_indices[i]
        end_idx = valid_indices[i + 1]
        gap_size = end_idx - start_idx - 1
        
        if gap_size > 0 and gap_size <= max_gap_size:
            start_val = values[i]
            end_val = values[i + 1]
            
            for j in range(1, gap_size + 1):
                alpha = j / (gap_size + 1)
                result[start_idx + j] = start_val + alpha * (end_val - start_val)
    
    return result