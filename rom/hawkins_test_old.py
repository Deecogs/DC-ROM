# rom/hawkins_test.py
from rom.base_test import ROMTest
from utils.angle_calculator import angle_between_points
import cv2

class HawkinsTest(ROMTest):
    def process_frame(self, frame):
        # Detect pose
        results = self.pose_detector.detect_pose(frame)
        if not results.pose_landmarks:
            return frame, None
            
        # Get landmark coordinates
        x_shoulder, y_shoulder, _ = self.pose_detector.get_landmark_coordinates(
            frame, results, self.pose_detector.mp_pose.PoseLandmark.LEFT_SHOULDER)
        x_elbow, y_elbow, _ = self.pose_detector.get_landmark_coordinates(
            frame, results, self.pose_detector.mp_pose.PoseLandmark.LEFT_ELBOW)
        x_wrist, y_wrist, _ = self.pose_detector.get_landmark_coordinates(
            frame, results, self.pose_detector.mp_pose.PoseLandmark.LEFT_WRIST)
            
        if all([x_shoulder, x_elbow, x_wrist]):
            # Calculate ROM data
            rom_data = self.calculate_rom(
                (x_shoulder, y_shoulder),
                (x_elbow, y_elbow),
                (x_wrist, y_wrist)
            )
            
            # Visualize results
            frame = self.visualize_results(frame, rom_data)
            
            return frame, rom_data
        
        return frame, None
        
    def calculate_rom(self, shoulder, elbow, wrist):
        # Calculate angles
        _, horizontal_angle = angle_between_points(elbow[0], elbow[1], wrist[0], wrist[1])
        vertical_angle = 90 - horizontal_angle
        
        return {
            'shoulder': shoulder,
            'elbow': elbow,
            'wrist': wrist,
            'angle': horizontal_angle,
            'vertical_angle': vertical_angle
        }
        
    def visualize_results(self, frame, rom_data):
        if not rom_data:
            return frame
            
        # Draw joint connections
        frame = self.visualizer.draw_diamond(
            frame,
            rom_data['elbow'][0], rom_data['elbow'][1],
            rom_data['wrist'][0], rom_data['wrist'][1],
            rom_data['shoulder'][0], rom_data['shoulder'][1]
        )
        
        # Draw ROM guides
        frame, fore_arm_length = self.visualizer.draw_rom_guides(
            frame,
            rom_data['elbow'][0], rom_data['elbow'][1],
            rom_data['wrist'][0], rom_data['wrist'][1]
        )
        
        # Add angle annotations
        self.visualizer.draw_angle_text(
            frame,
            rom_data['angle'],
            (rom_data['elbow'][0] - fore_arm_length, rom_data['elbow'][1] - 20),
            "Horizontal angle:"
        )
        
        self.visualizer.draw_angle_text(
            frame,
            rom_data['vertical_angle'],
            (rom_data['elbow'][0] - 20, rom_data['elbow'][1] - fore_arm_length),
            "Vertical angle:"
        )
        
        return frame