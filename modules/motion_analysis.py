from modules.utils import calculate_angle

def analyze_elbow_flexion(frame, landmarks):
    left_shoulder = landmarks[11]
    left_elbow = landmarks[13]
    left_wrist = landmarks[15]

    x_shoulder, y_shoulder = int(left_shoulder.x * frame.shape[1]), int(left_shoulder.y * frame.shape[0])
    x_elbow, y_elbow = int(left_elbow.x * frame.shape[1]), int(left_elbow.y * frame.shape[0])
    x_wrist, y_wrist = int(left_wrist.x * frame.shape[1]), int(left_wrist.y * frame.shape[0])

    angle = calculate_angle(x_shoulder, y_shoulder, x_elbow, y_elbow, x_wrist, y_wrist)
    return angle
