import math
import cv2

class HawkinsTest:
    def __init__(self, pose_detector, visualizer):
        self.pose_detector = pose_detector
        self.visualizer = visualizer
        
    def calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points."""
        angle = math.degrees(math.atan2(p3[1]-p2[1], p3[0]-p2[0]) - 
                           math.atan2(p1[1]-p2[1], p1[0]-p2[0]))
        return angle + 360 if angle < 0 else angle
        
    def process_frame(self, frame):
        """Process a single frame for Hawkins test."""
        landmarks = self.pose_detector.find_pose(frame)
        
        if not landmarks:
            return frame, {"error": "No pose detected"}
            
        coords = self.pose_detector.get_landmark_coordinates(frame, landmarks)
        
        # Get relevant landmarks for Hawkins test
        shoulder = coords[11]  # Left shoulder
        elbow = coords[13]    # Left elbow
        wrist = coords[15]    # Left wrist
        
        # Calculate angles
        arm_angle = self.calculate_angle(shoulder, elbow, wrist)
        
        # Visualize
        self.visualizer.draw_landmark_point(frame, shoulder[0], shoulder[1], 'white')
        self.visualizer.draw_landmark_point(frame, elbow[0], elbow[1], 'white')
        self.visualizer.draw_landmark_point(frame, wrist[0], wrist[1], 'white')
        
        self.visualizer.draw_angle(frame, shoulder, elbow, wrist, arm_angle)
        
        # Add reference lines
        if elbow[1] > wrist[1]:
            self.visualizer.put_text(frame, "Hand above elbow", (10, 60), color='green')
        else:
            self.visualizer.put_text(frame, "Hand below elbow", (10, 60), color='red')
            
        rom_data = {
            "test": "hawkins",
            "arm_angle": arm_angle,
            "shoulder_height": shoulder[1],
            "elbow_height": elbow[1],
            "wrist_height": wrist[1]
        }
        
        return frame, rom_data