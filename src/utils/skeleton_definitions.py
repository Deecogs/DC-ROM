# MediaPipe pose landmark indices
MEDIAPIPE_KEYPOINTS = {
    'nose': 0,
    'left_eye_inner': 1,
    'left_eye': 2,
    'left_eye_outer': 3,
    'right_eye_inner': 4,
    'right_eye': 5,
    'right_eye_outer': 6,
    'left_ear': 7,
    'right_ear': 8,
    'mouth_left': 9,
    'mouth_right': 10,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_pinky': 17,
    'right_pinky': 18,
    'left_index': 19,
    'right_index': 20,
    'left_thumb': 21,
    'right_thumb': 22,
    'left_hip': 23,
    'right_hip': 24,
    'left_knee': 25,
    'right_knee': 26,
    'left_ankle': 27,
    'right_ankle': 28,
    'left_heel': 29,
    'right_heel': 30,
    'left_foot_index': 31,
    'right_foot_index': 32
}

# Skeleton connections for visualization
MEDIAPIPE_CONNECTIONS = [
    # Face
    (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye
    (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye
    (9, 10),  # Mouth
    
    # Upper body
    (11, 12),  # Shoulders
    (11, 13), (13, 15),  # Left arm
    (12, 14), (14, 16),  # Right arm
    (11, 23), (12, 24), (23, 24),  # Torso
    
    # Lower body
    (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),  # Left leg
    (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),  # Right leg
]

# Mapping to common names
KEYPOINT_MAP = {
    'nose': 'nose',
    'left_shoulder': 'left_shoulder',
    'right_shoulder': 'right_shoulder',
    'left_elbow': 'left_elbow',
    'right_elbow': 'right_elbow',
    'left_wrist': 'left_wrist',
    'right_wrist': 'right_wrist',
    'left_hip': 'left_hip',
    'right_hip': 'right_hip',
    'left_knee': 'left_knee',
    'right_knee': 'right_knee',
    'left_ankle': 'left_ankle',
    'right_ankle': 'right_ankle',
    'left_heel': 'left_heel',
    'right_heel': 'right_heel',
    'left_toe': 'left_foot_index',
    'right_toe': 'right_foot_index',
}

def get_neck_position(keypoints):
    """Calculate neck position as midpoint between shoulders"""
    if 'left_shoulder' not in keypoints or 'right_shoulder' not in keypoints:
        return {'x': 0, 'y': 0, 'confidence': 0}
    
    left_shoulder = keypoints['left_shoulder']
    right_shoulder = keypoints['right_shoulder']
    
    return {
        'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
        'y': (left_shoulder['y'] + right_shoulder['y']) / 2,
        'confidence': (left_shoulder['confidence'] + right_shoulder['confidence']) / 2
    }

def get_hip_center(keypoints):
    """Calculate hip center as midpoint between hips"""
    if 'left_hip' not in keypoints or 'right_hip' not in keypoints:
        return {'x': 0, 'y': 0, 'confidence': 0}
    
    left_hip = keypoints['left_hip']
    right_hip = keypoints['right_hip']
    
    return {
        'x': (left_hip['x'] + right_hip['x']) / 2,
        'y': (left_hip['y'] + right_hip['y']) / 2,
        'confidence': (left_hip['confidence'] + right_hip['confidence']) / 2
    }