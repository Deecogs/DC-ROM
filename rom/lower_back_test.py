import math
import cv2
import numpy as np
from collections import deque

class LowerBackFlexionTest:
    def __init__(self, pose_detector, visualizer, window_size=100):
        self.pose_detector = pose_detector
        self.visualizer = visualizer
        self.ready_time = 0
        self.required_ready_time = 20
        self.is_ready = False
        self.angle_buffer = deque(maxlen=window_size)  # Buffer for last N angles
        self.min_angle = float('inf')  # Initialize with infinity
        self.max_angle = float('-inf')  # Initialize with negative infinity
        self.key_points = [
            11,  # Left shoulder
            12,  # Right shoulder
            23,  # Left hip
            24,  # Right hip
            25,  # Left knee
            26,  # Right knee
            27,  # Left ankle
            28   # Right ankle
        ]

    # @staticmethod
    # def calculate_angle(p1, p2, p3):
    #     """Calculate angle between three points."""
    #     angle = math.degrees(math.atan2(p3[1] - p2[1], p3[0] - p2[0]) -
    #                          math.atan2(p1[1] - p2[1], p1[0] - p2[0]))
    #     return angle + 360 if angle < 0 else angle
    @staticmethod
    def calculate_angle(p1, p2, p3):
        """
        Calculate the angle between three points.
        p2 is the vertex point.
        """
        # Convert points to NumPy arrays
        p1 = np.array(p1[:2])  # Only take x, y coordinates
        p2 = np.array(p2[:2])
        p3 = np.array(p3[:2])

        # Vectors from the vertex
        vector1 = p1 - p2
        vector2 = p3 - p2

        # Compute the cosine of the angle
        cosine_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # Handle numerical inaccuracies

        # Compute the angle in degrees
        angle = np.degrees(np.arccos(cosine_angle))
        return angle

    def check_initial_position(self, frame, coords):
        """
        Check if the person is in the correct starting position.
        Returns: (bool, str) - (is_position_valid, message)
        """
        h, w, _ = frame.shape
        messages = []
        is_valid = True

        # Check if all required points are detected
        for point in self.key_points:
            if point not in coords:
                return False, "Cannot detect full body. Please step back."

        # Check if person is facing the camera (using shoulder width)
        left_shoulder = coords[11]
        right_shoulder = coords[12]
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
        if shoulder_width < w * 0.15:
            messages.append("Turn to face the camera")
            is_valid = False

        # Check if person is too close or too far
        body_height = abs(coords[11][1] - coords[27][1])
        if body_height < h * 0.5:
            messages.append("Step closer to the camera")
            is_valid = False
        elif body_height > h * 0.9:
            messages.append("Step back from the camera")
            is_valid = False

        # Check if person is centered
        center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        if center_x < w * 0.3:
            messages.append("Move right")
            is_valid = False
        elif center_x > w * 0.7:
            messages.append("Move left")
            is_valid = False

        # Check if person is standing straight
        left_hip = coords[23]
        right_hip = coords[24]
        hip_angle = self.calculate_angle(left_shoulder,
                                         ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2),
                                         right_shoulder)
        if not (85 <= hip_angle <= 95):
            messages.append("Stand straight")
            is_valid = False

        message = " | ".join(messages) if messages else "Good starting position"
        return is_valid, message

    def draw_pose_guidance(self, frame, message):
        """Draw guidance overlay on frame."""
        h, w, _ = frame.shape

        # Draw semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 100), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # Draw guidance text
        self.visualizer.put_text(
            frame,
            f"Position Guide: {message}",
            (20, h - 60),
            color='white',
            scale=1.0
        )

        # Draw progress bar if in correct position
        if self.ready_time > 0:
            progress = (self.ready_time / self.required_ready_time) * (w - 40)
            cv2.rectangle(frame, (20, h - 30), (w - 20, h - 20), (255, 255, 255), 2)
            cv2.rectangle(frame, (20, h - 30), (int(20 + progress), h - 20), (0, 255, 0), -1)

        return frame

    def update_rom(self, angle):
        """Update ROM based on a sliding window of the last N angles."""
        # Add the new angle to the buffer
        self.angle_buffer.append(angle)

        # Compute the min and max over the buffer
        self.min_angle = min(self.angle_buffer)
        self.max_angle = max(self.angle_buffer)
    def process_frame(self, frame):
        """Process a single frame for Lower Back Flexion test."""
        landmarks = self.pose_detector.find_pose(frame)

        if not landmarks:
            return frame, {"error": "No pose detected"}

        coords = self.pose_detector.get_landmark_coordinates(frame, landmarks)

        # First check initial position
        is_valid_position, guidance_message = self.check_initial_position(frame, coords)

        # Update ready state
        if is_valid_position:
            self.ready_time += 1
            if self.ready_time >= self.required_ready_time:
                self.is_ready = True
        else:
            self.ready_time = 0
            self.is_ready = False

        # Draw position guidance
        frame = self.draw_pose_guidance(frame, guidance_message)

        # Get relevant landmarks for Lower Back Flexion
        shoulder = coords[11]  # Left shoulder
        hip = coords[23]      # Left hip
        knee = coords[25]     # Left knee

        # Calculate trunk angle
        trunk_angle = self.calculate_angle(shoulder, hip, knee)

        # Update ROM
        self.update_rom(trunk_angle)

        # Visualize landmarks and angles
        self.visualizer.draw_landmark_point(frame, shoulder[0], shoulder[1], 'white')
        self.visualizer.draw_landmark_point(frame, hip[0], hip[1], 'white')
        self.visualizer.draw_landmark_point(frame, knee[0], knee[1], 'white')

        self.visualizer.draw_angle(frame, shoulder, hip, knee, trunk_angle)

        # Add feedback based on trunk angle
        posture_message = ""
        if self.is_ready:
            if 80 <= trunk_angle <= 100:
                posture_message = "Good posture"
                self.visualizer.put_text(frame, posture_message, (10, 60), color='green')
            else:
                posture_message = "Adjust posture"
                self.visualizer.put_text(frame, posture_message, (10, 60), color='red')

        rom_data = {
            "test": "lower_back_flexion",
            "is_ready": self.is_ready,
            "trunk_angle": trunk_angle,
            "ROM": [self.min_angle, self.max_angle],
            "position_valid": is_valid_position,
            "guidance": guidance_message,
            "posture_message": posture_message,
            "ready_progress": (self.ready_time / self.required_ready_time) * 100,
            "shoulder_position": (shoulder[0], shoulder[1]),
            "hip_position": (hip[0], hip[1]),
            "knee_position": (knee[0], knee[1])
        }

        return frame, rom_data