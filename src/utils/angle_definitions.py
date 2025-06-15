import numpy as np

# Angle definitions following Sports2D conventions
JOINT_ANGLES = {
    'right_ankle': {
        'points': ['right_knee', 'right_ankle', 'right_toe', 'right_heel'],
        'type': 'dorsiflexion',
        'offset': 90,
        'scale': 1
    },
    'left_ankle': {
        'points': ['left_knee', 'left_ankle', 'left_toe', 'left_heel'],
        'type': 'dorsiflexion',
        'offset': 90,
        'scale': 1
    },
    'right_knee': {
        'points': ['right_ankle', 'right_knee', 'right_hip'],
        'type': 'flexion',
        'offset': -180,
        'scale': 1
    },
    'left_knee': {
        'points': ['left_ankle', 'left_knee', 'left_hip'],
        'type': 'flexion',
        'offset': -180,
        'scale': 1
    },
    'right_hip': {
        'points': ['right_knee', 'right_hip', 'hip_center', 'neck'],
        'type': 'flexion',
        'offset': 0,
        'scale': -1
    },
    'left_hip': {
        'points': ['left_knee', 'left_hip', 'hip_center', 'neck'],
        'type': 'flexion',
        'offset': 0,
        'scale': -1
    },
    'right_shoulder': {
        'points': ['right_elbow', 'right_shoulder', 'hip_center', 'neck'],
        'type': 'flexion',
        'offset': 0,
        'scale': -1
    },
    'left_shoulder': {
        'points': ['left_elbow', 'left_shoulder', 'hip_center', 'neck'],
        'type': 'flexion',
        'offset': 0,
        'scale': -1
    },
    'right_elbow': {
        'points': ['right_wrist', 'right_elbow', 'right_shoulder'],
        'type': 'flexion',
        'offset': 180,
        'scale': -1
    },
    'left_elbow': {
        'points': ['left_wrist', 'left_elbow', 'left_shoulder'],
        'type': 'flexion',
        'offset': 180,
        'scale': -1
    }
}

SEGMENT_ANGLES = {
    'right_foot': {
        'points': ['right_toe', 'right_heel'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'left_foot': {
        'points': ['left_toe', 'left_heel'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'right_shank': {
        'points': ['right_ankle', 'right_knee'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'left_shank': {
        'points': ['left_ankle', 'left_knee'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'right_thigh': {
        'points': ['right_knee', 'right_hip'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'left_thigh': {
        'points': ['left_knee', 'left_hip'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'pelvis': {
        'points': ['left_hip', 'right_hip'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'trunk': {
        'points': ['neck', 'hip_center'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'shoulders': {
        'points': ['left_shoulder', 'right_shoulder'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'right_arm': {
        'points': ['right_elbow', 'right_shoulder'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'left_arm': {
        'points': ['left_elbow', 'left_shoulder'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'right_forearm': {
        'points': ['right_wrist', 'right_elbow'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    },
    'left_forearm': {
        'points': ['left_wrist', 'left_elbow'],
        'type': 'horizontal',
        'offset': 0,
        'scale': -1
    }
}

def calculate_angle_2d(p1, p2, p3=None):
    """
    Calculate angle between vectors or with horizontal.
    For 3 points: angle at p2
    For 2 points: angle with horizontal
    """
    if p3 is None:
        # Segment angle with horizontal
        dx = p2['x'] - p1['x']
        dy = p2['y'] - p1['y']
        angle = np.degrees(np.arctan2(dy, dx))
    else:
        # Joint angle between three points
        v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y']])
        v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
        
        # Handle zero vectors
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return np.nan
            
        cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine_angle))
    
    return angle

def calculate_ankle_angle(knee, ankle, toe, heel):
    """Special calculation for ankle dorsiflexion"""
    # Vector from heel to toe
    foot_vector = np.array([toe['x'] - heel['x'], toe['y'] - heel['y']])
    # Vector from ankle to knee
    shank_vector = np.array([knee['x'] - ankle['x'], knee['y'] - ankle['y']])
    
    if np.linalg.norm(foot_vector) == 0 or np.linalg.norm(shank_vector) == 0:
        return np.nan
    
    # Calculate angle
    cosine_angle = np.dot(foot_vector, shank_vector) / (np.linalg.norm(foot_vector) * np.linalg.norm(shank_vector))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))
    
    return angle