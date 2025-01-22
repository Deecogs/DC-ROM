import cv2
import math

class PoseVisualizer:
    def __init__(self):
        self.colors = {
            'white': (255, 255, 255),
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0)
        }

    def draw_landmark_point(self, frame, x, y, color='white', size=3):
        cv2.circle(frame, (x, y), size, self.colors[color], -1)
        
    def draw_connection(self, frame, start_point, end_point, color='white', thickness=2):
        cv2.line(frame, start_point, end_point, self.colors[color], thickness)
        
    def put_text(self, frame, text, position, color='white', scale=0.8, thickness=2):
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, scale, self.colors[color], thickness)

    def draw_angle(self, frame, point1, point2, point3, angle):
        """Draw an angle between three points with its value."""
        cv2.line(frame, point1[:2], point2[:2], self.colors['blue'], 2)
        cv2.line(frame, point2[:2], point3[:2], self.colors['blue'], 2)
        
        # Add angle text
        text_position = (point2[0] - 50, point2[1] - 20)
        self.put_text(frame, f"{angle:.1f}°", text_position)