import mediapipe as mp
import cv2

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1)
        self.mp_drawing = mp.solutions.drawing_utils
        
    def find_pose(self, frame):
        """Process frame and return pose landmarks."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        return results.pose_landmarks if results.pose_landmarks else None
    
    def get_landmark_coordinates(self, frame, landmarks):
        """Convert normalized landmarks to pixel coordinates."""
        h, w, _ = frame.shape
        coordinates = {}
        
        if landmarks:
            for idx, landmark in enumerate(landmarks.landmark):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                z = landmark.z
                coordinates[idx] = (x, y, z)
                
        return coordinates