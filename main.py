import cv2
from modules.pose_estimation import PoseEstimator
from modules.visualization import draw_overlay, draw_diamond, annotate_elbow_angle
from modules.motion_analysis import analyze_elbow_flexion
from config.settings import VIDEO_PATH, OUTPUT_PATH, OVERLAY_PATH, API_ENDPOINT

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    pose_estimator = PoseEstimator()

    # Load overlay
    overlay_image = cv2.imread(OVERLAY_PATH, cv2.IMREAD_UNCHANGED)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process pose landmarks
        landmarks = pose_estimator.process_frame(frame)

        # Draw overlay
        frame = draw_overlay(frame, overlay_image)

        if landmarks:
            # Analyze and visualize elbow flexion
            flexion_angle = analyze_elbow_flexion(frame, landmarks)
            if flexion_angle is not None:
                draw_diamond(frame, landmarks)
                annotate_elbow_angle(frame, flexion_angle)

        out.write(frame)
        cv2.imshow('ROM Tool', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
