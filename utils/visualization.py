# utils/visualization.py
import cv2
import numpy as np

class PoseVisualizer:
    @staticmethod
    def draw_diamond(img, x_elbow, y_elbow, x_wrist, y_wrist, x_shoulder, y_shoulder):
        offset = 3
        
        # Draw joint points
        for x, y in [(x_elbow, y_elbow), (x_wrist, y_wrist), (x_shoulder, y_shoulder)]:
            cv2.rectangle(img, 
                         (x-offset, y-offset), 
                         (x+offset, y+offset), 
                         (255, 255, 255), 
                         -1)

        # Draw lines between joints
        cv2.line(img, (x_shoulder, y_shoulder), (x_elbow, y_elbow), (0, 255, 0), 2)
        cv2.line(img, (x_elbow, y_elbow), (x_wrist, y_wrist), (0, 255, 0), 2)

        return img

    @staticmethod
    def draw_rom_guides(img, x_elbow, y_elbow, x_wrist, y_wrist):
        # Calculate forearm length
        fore_arm_length = int(((x_elbow - x_wrist) ** 2 + (y_elbow - y_wrist) ** 2)**(1/2))
        
        # Draw vertical reference line
        cv2.line(img, 
                 (x_elbow, y_elbow), 
                 (x_elbow, y_elbow-fore_arm_length), 
                 (255, 0, 0), 
                 2, 
                 cv2.LINE_AA)
        
        # Draw horizontal reference line
        cv2.line(img, 
                 (x_elbow, y_elbow), 
                 (x_elbow-fore_arm_length, y_elbow), 
                 (0, 0, 255), 
                 2, 
                 cv2.LINE_AA)
        
        return img, fore_arm_length

    @staticmethod
    def draw_angle_text(img, angle_data, position, text_prefix="Angle:"):
        cv2.putText(img,
                   f"{text_prefix} {angle_data:.1f}°",
                   position,
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.7,
                   (255, 255, 255),
                   2,
                   cv2.LINE_AA)
        return img