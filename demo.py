# demo.py
import cv2
import numpy as np
from utils.pose_detector import PoseDetector
from utils.visualization import PoseVisualizer
from rom.hawkins_test import HawkinsTest
import argparse

def main():
    parser = argparse.ArgumentParser(description='ROM Calculator Demo')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--video', type=str, help='Path to video file (optional)')
    args = parser.parse_args()

    # Initialize camera/video
    if args.video:
        cap = cv2.VideoCapture(args.video)
    else:
        cap = cv2.VideoCapture(args.camera)

    # Check if camera/video opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera/video")
        return

    # Get frame properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize components
    pose_detector = PoseDetector()
    visualizer = PoseVisualizer()
    hawkins_test = HawkinsTest(pose_detector, visualizer)

    # Create window
    window_name = 'ROM Calculator Demo - Press Q to quit'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, frame_width, frame_height)

    while True:
        ret, frame = cap.read()
        if not ret:
            if args.video:  # If video ends, break
                break
            continue  # If camera frame is not ready, skip

        # Process frame
        processed_frame, rom_data = hawkins_test.process_frame(frame)

        # Show instructions
        cv2.putText(processed_frame, 
                   "Stand in the center and raise your left arm", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 
                   (255, 255, 255), 
                   2)

        # Display frame
        cv2.imshow(window_name, processed_frame)

        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()