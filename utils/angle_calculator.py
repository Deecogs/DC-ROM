# utils/angle_calculator.py
import math
import numpy as np

def calculate_angle(a, b, c):
    """Calculate angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)

def angle_between_points(x1, y1, x2, y2):
    """Calculate angle between point and vertical."""
    if x2 == x1:
        x1 = x1 + 1
    slope = (y2 - y1) / (x2 - x1)
    theta_radians = math.atan(slope)
    theta_degrees = math.degrees(theta_radians)
    return theta_radians, theta_degrees