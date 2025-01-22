import cv2
import mediapipe as mp
import numpy as np

class LowerBackFlexionTest:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.roi = (0, 0, 2400, 3600)  # Example ROI, can be customized

    def _diamond_display(self, img, points):
        """Draw diamonds and connections on the key points."""
        offset = 3
        for point in points.values():
            x, y = point
            img = cv2.rectangle(img, (int(x - offset), int(y - offset)),
                                (int(x + offset), int(y + offset)), (255, 255, 255), -1)

        connections = [
            ("hip", "knee"), ("knee", "ankle"), ("shoulder", "hip"),
        ]
        for start, end in connections:
            x1, y1 = points[start]
            x2, y2 = points[end]
            img = cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        return img

    @staticmethod
    def _calculate_angle(a, b, c):
        """Calculate angle between three points."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(cosine_angle))

    def process_frame(self, frame):
        """Process the frame for lower back flexion test analysis."""
        h, w, _ = frame.shape

        # Convert the frame for Mediapipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            key_points = {
                "shoulder": (
                    (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x +
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x) * w / 2,
                    (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) * h / 2
                ),
                "hip": (
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * h
                ),
                "knee": (
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y * h
                ),
                "ankle": (
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h
                )
            }

            # Draw diamonds and connections
            frame = self._diamond_display(frame, key_points)

            # Calculate knee angle
            left_knee_angle = self._calculate_angle(
                [key_points["hip"][0], key_points["hip"][1]],
                [key_points["knee"][0], key_points["knee"][1]],
                [key_points["ankle"][0], key_points["ankle"][1]],
            )
            cv2.putText(frame, f"Knee Angle: {int(left_knee_angle)}",
                        (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            if left_knee_angle < 160:
                cv2.putText(frame, "Warning: Your knees are bending! Keep them straight.",
                            (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        return frame

    def analyze_video(self, video_path, output_path):
        """Analyze the video and save annotated output."""
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Analyze the frame
            annotated_frame = self.process_frame(frame)
            out.write(annotated_frame)

        cap.release()
        out.release()
