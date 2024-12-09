import math

def calculate_angle(x1, y1, x2, y2, x3, y3):
    vector1 = (x1 - x2, y1 - y2)
    vector2 = (x3 - x2, y3 - y2)
    dot = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    magnitude = math.sqrt(vector1[0]**2 + vector1[1]**2) * math.sqrt(vector2[0]**2 + vector2[1]**2)
    angle = math.degrees(math.acos(dot / magnitude))
    return angle
