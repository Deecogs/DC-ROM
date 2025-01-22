import cv2
import mediapipe as mp
import math

class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1)
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.keypoint_names = [
            "NOSE",
            "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
            "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
            "LEFT_EAR", "RIGHT_EAR",
            "MOUTH_LEFT", "MOUTH_RIGHT",
            "LEFT_SHOULDER", "RIGHT_SHOULDER",
            "LEFT_ELBOW", "RIGHT_ELBOW",
            "LEFT_WRIST", "RIGHT_WRIST",
            "LEFT_PINKY", "RIGHT_PINKY",
            "LEFT_INDEX", "RIGHT_INDEX",
            "LEFT_THUMB", "RIGHT_THUMB",
            "LEFT_HIP", "RIGHT_HIP",
            "LEFT_KNEE", "RIGHT_KNEE",
            "LEFT_ANKLE", "RIGHT_ANKLE",
            "LEFT_HEEL", "RIGHT_HEEL",
            "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
        ]

    def vector_magnitude(self, vector):
        return math.sqrt(vector[0] ** 2 + vector[1] ** 2)

    def dot_product(self, vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def angle_between_points(self, x1, y1, x2, y2):
        if x2 == x1:
            x1 = x1 + 1
        slope = (y2 - y1) / (x2 - x1)
        theta_radians = math.atan(slope)
        theta_degrees = math.degrees(theta_radians)
        return theta_radians, theta_degrees

    def diamond_display(self, img, x_elbow, y_elbow, x_wrist, y_wrist, x_shoulder, y_shoulder):
        offset = 3
        img = cv2.rectangle(img, (x_elbow-offset, y_elbow-offset), (x_elbow+offset, y_elbow+offset), (255, 255, 255), -1)
        img = cv2.rectangle(img, (x_wrist-offset, y_wrist-offset), (x_wrist+offset, y_wrist+offset), (255, 255, 255), -1)
        img = cv2.rectangle(img, (x_shoulder-offset, y_shoulder-offset), (x_shoulder+offset, y_shoulder+offset), (255, 255, 255), -1)

        img = cv2.line(img, (x_elbow-offset, y_elbow-offset), (x_wrist, y_wrist), (0, 2, 0), 1)
        img = cv2.line(img, (x_elbow-offset, y_elbow+offset), (x_wrist, y_wrist), (0, 2, 0), 1)
        img = cv2.line(img, (x_elbow+offset, y_elbow-offset), (x_wrist, y_wrist), (0, 2, 0), 1)
        img = cv2.line(img, (x_elbow+offset, y_elbow+offset), (x_wrist, y_wrist), (0, 2, 0), 1)

        img = cv2.line(img, (x_shoulder-offset, y_shoulder-offset), (x_elbow, y_elbow), (0, 2, 0), 1)
        img = cv2.line(img, (x_shoulder-offset, y_shoulder+offset), (x_elbow, y_elbow), (0, 2, 0), 1)
        img = cv2.line(img, (x_shoulder+offset, y_shoulder-offset), (x_elbow, y_elbow), (0, 2, 0), 1)
        img = cv2.line(img, (x_shoulder+offset, y_shoulder+offset), (x_elbow, y_elbow), (0, 2, 0), 1)
        return img

    def elbow_point(self, img, x_elbow, y_elbow, x_wrist, y_wrist):
        fore_arm_length = int(((x_elbow - x_wrist) ** 2 + (y_elbow - y_wrist) ** 2)**(1/2))
        fore_arm_mp = (int((x_elbow+x_wrist)/2), int((y_elbow+y_wrist)/2))
        vl_mp = (x_elbow, int((y_elbow+y_elbow-fore_arm_length)/2))
        hl_mp = int((x_elbow+x_elbow-fore_arm_length)/2), y_elbow

        label = "Hand bent beyond out of the Vertical Line"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

        if y_wrist > y_elbow:
            img = cv2.rectangle(img, (x_elbow-fore_arm_length, y_elbow+10), (x_elbow-fore_arm_length + w, y_elbow+20), (80, 80, 255), -1)
            cv2.putText(img, "Hand bent beneath the Horizontal Line", (x_elbow-fore_arm_length, y_elbow+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 5, 0), 2)
        elif x_wrist > x_elbow:
            img = cv2.rectangle(img, (x_wrist, y_wrist - 30-15), (x_wrist + w, y_wrist - 30), (128, 128, 255), -1)
            cv2.putText(img, "Hand bent beyond out of the Vertical Line", (x_wrist, y_wrist - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 5, 0), 2)

        img = cv2.line(img, (x_elbow, y_elbow), (x_elbow, y_elbow-fore_arm_length), (2, 200, 200), 3)
        img = cv2.line(img, (x_elbow, y_elbow), (x_elbow-fore_arm_length, y_elbow), (2, 200, 200), 3)
        img = cv2.line(img, (x_elbow, y_elbow), (x_elbow, y_elbow-fore_arm_length), (0, 200, 0), 1)
        img = cv2.line(img, (x_elbow, y_elbow), (x_elbow-fore_arm_length, y_elbow), (0, 200, 0), 1)
        img = cv2.line(img, vl_mp, fore_arm_mp, (200, 0, 0), 2)
        img = cv2.line(img, hl_mp, fore_arm_mp, (0, 0, 250), 2)
        
        _, ang = self.angle_between_points(x_elbow, y_elbow, x_wrist, y_wrist)
        l_ang = 90 - ang
        cv2.putText(img, f"angle between horizontal line and hand: {ang:.2f}", (x_elbow-fore_arm_length, y_elbow - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 5, 0), 2)
        cv2.putText(img, f"angle between vertical and hand: {l_ang:.2f}", (x_elbow-20, y_elbow - fore_arm_length), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 5, 0), 2)
        return img

    def process_video(self, video_source=0, output_path=None, overlay_image_path=None):
        cap = cv2.VideoCapture(video_source)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Initialize video writer if output path is provided
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        # Load and process overlay image if provided
        overlay_alpha = None
        resized_overlay = None
        if overlay_image_path:
            overlay_image = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)
            if overlay_image.shape[2] == 4:
                overlay_alpha = overlay_image[:, :, 3] / 255.0
                overlay_rgb = overlay_image[:, :, :3]
            else:
                overlay_rgb = overlay_image

            overlay_width = int(frame_width * 0.25)
            overlay_height = int(overlay_image.shape[0] * overlay_width / overlay_image.shape[1])
            resized_overlay = cv2.resize(overlay_rgb, (overlay_width, overlay_height))
            if overlay_alpha is not None:
                resized_overlay_alpha = cv2.resize(overlay_alpha, (overlay_width, overlay_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            # Process overlay if available
            if resized_overlay is not None:
                y1, y2 = 0, overlay_height
                x1, x2 = 0, overlay_width
                roi = frame[y1:y2, x1:x2]
                
                if overlay_alpha is not None:
                    for c in range(0, 3):
                        roi[:, :, c] = (resized_overlay_alpha * resized_overlay[:, :, c] +
                                      (1 - resized_overlay_alpha) * roi[:, :, c])
                else:
                    roi = resized_overlay
                frame[y1:y2, x1:x2] = roi

            # Process pose
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                left_shoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                left_elbow = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW]
                left_wrist = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]

                x_shoulder = int(left_shoulder.x * frame.shape[1])
                y_shoulder = int(left_shoulder.y * frame.shape[0])
                x_elbow = int(left_elbow.x * frame.shape[1])
                y_elbow = int(left_elbow.y * frame.shape[0])
                x_wrist = int(left_wrist.x * frame.shape[1])
                y_wrist = int(left_wrist.y * frame.shape[0])

                frame = self.diamond_display(frame, x_elbow, y_elbow, x_wrist, y_wrist, x_shoulder, y_shoulder)
                frame = self.elbow_point(frame, x_elbow, y_elbow, x_wrist, y_wrist)

            if out:
                out.write(frame)

            cv2.imshow('Deecogs Model for Hawkins', frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        if out:
            out.release()
        cap.release()
        cv2.destroyAllWindows()

# from pose_estimator import PoseEstimator

def main():
    # Initialize the pose estimator
    pose_estimator = PoseEstimator()
    
    # Process video from webcam (default)
    pose_estimator.process_video(overlay_image_path="/Users/chandansharma/Desktop/workspace/metashape/projects/dc-pose/DC-ROM/assests/overlay_images/hawkins_test.png")
    
    # Or process video from file with output and overlay
    # pose_estimator.process_video(
    #     video_source="path/to/input/video.mp4",
    #     output_path="path/to/output/video.mp4",
    #     overlay_image_path="path/to/overlay/image.png"
    # )

if __name__ == "__main__":
    main()