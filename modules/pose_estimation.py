import mediapipe as mp
import cv2

class PoseEstimator:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)
        self.drawing_utils = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        return results.pose_landmarks.landmark if results.pose_landmarks else None
