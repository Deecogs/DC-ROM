import cv2
import math
from rom.base_test import ROMTest

class HawkinsTest(ROMTest):
    def process_frame(self, frame):
        # Detect pose
        results = self.pose_detector.detect_pose(frame)
        if not results.pose_landmarks:
            return frame, None

        # Extract key landmarks
        x_shoulder, y_shoulder, _ = self.pose_detector.get_landmark_coordinates(
            frame, results, self.pose_detector.mp_pose.PoseLandmark.LEFT_SHOULDER)
        x_elbow, y_elbow, _ = self.pose_detector.get_landmark_coordinates(
            frame, results, self.pose_detector.mp_pose.PoseLandmark.LEFT_ELBOW)
        x_wrist, y_wrist, _ = self.pose_detector.get_landmark_coordinates(
            frame, results, self.pose_detector.mp_pose.PoseLandmark.LEFT_WRIST)

        if all([x_shoulder, y_shoulder, x_elbow, y_elbow, x_wrist, y_wrist]):
            # Calculate angles and ROM data
            rom_data = self.calculate_rom(
                (x_shoulder, y_shoulder),
                (x_elbow, y_elbow),
                (x_wrist, y_wrist)
            )

            # Visualize results on the frame
            frame = self.visualize_results(frame, rom_data)
            return frame, rom_data

        return frame, None

    def calculate_rom(self, shoulder, elbow, wrist):
        # Calculate angles
        upper_arm_angle = self.calculate_angle(shoulder, elbow, wrist)
        horizontal_angle = self.calculate_horizontal_angle(elbow, wrist)

        return {
            'shoulder': shoulder,
            'elbow': elbow,
            'wrist': wrist,
            'upper_arm_angle': upper_arm_angle,
            'horizontal_angle': horizontal_angle
        }

    @staticmethod
    def calculate_angle(a, b, c):
        ax, ay = a
        bx, by = b
        cx, cy = c
        
        ab = [ax - bx, ay - by]
        cb = [cx - bx, cy - by]

        dot_product = ab[0] * cb[0] + ab[1] * cb[1]
        magnitude_ab = math.sqrt(ab[0] ** 2 + ab[1] ** 2)
        magnitude_cb = math.sqrt(cb[0] ** 2 + cb[1] ** 2)

        if magnitude_ab * magnitude_cb == 0:
            return 0

        cos_theta = dot_product / (magnitude_ab * magnitude_cb)
        angle_radians = math.acos(max(-1, min(1, cos_theta)))  # Clamp to avoid numerical errors
        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    @staticmethod
    def calculate_horizontal_angle(elbow, wrist):
        ex, ey = elbow
        wx, wy = wrist

        if wx == ex:
            return 90 if wy < ey else -90

        slope = (wy - ey) / (wx - ex)
        angle_radians = math.atan(slope)
        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    def visualize_results(self, frame, rom_data):
        if not rom_data:
            return frame

        x_shoulder, y_shoulder = rom_data['shoulder']
        x_elbow, y_elbow = rom_data['elbow']
        x_wrist, y_wrist = rom_data['wrist']

        # Draw markers for joints
        self.draw_marker(frame, x_shoulder, y_shoulder, color=(0, 255, 255))
        self.draw_marker(frame, x_elbow, y_elbow, color=(255, 0, 0))
        self.draw_marker(frame, x_wrist, y_wrist, color=(0, 0, 255))

        # Draw limb connections
        cv2.line(frame, (x_shoulder, y_shoulder), (x_elbow, y_elbow), (255, 255, 0), 2)
        cv2.line(frame, (x_elbow, y_elbow), (x_wrist, y_wrist), (0, 255, 0), 2)

        # Annotate angles
        self.annotate_text(frame, f"Upper Arm Angle: {rom_data['upper_arm_angle']:.2f}", x_elbow - 50, y_elbow - 20)
        self.annotate_text(frame, f"Horizontal Angle: {rom_data['horizontal_angle']:.2f}", x_wrist + 10, y_wrist - 10)

        return frame

    @staticmethod
    def draw_marker(img, x, y, color=(0, 255, 0), size=5):
        cv2.circle(img, (x, y), size, color, -1)

    @staticmethod
    def annotate_text(img, text, x, y, font_scale=0.5, color=(0, 255, 0), thickness=1):
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
