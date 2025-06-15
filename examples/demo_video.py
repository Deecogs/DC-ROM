"""
Demo script for local testing with visualization
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.processing.frame_processor import FrameProcessor
from src.utils.skeleton_definitions import MEDIAPIPE_CONNECTIONS

def visualize_frame(frame, result):
    """Draw pose and angles on frame"""
    output = frame.copy()
    
    for person in result['persons']:
        # Draw skeleton
        keypoints = person['keypoints']
        
        # Draw connections
        for connection in MEDIAPIPE_CONNECTIONS:
            if connection[0] < len(keypoints) and connection[1] < len(keypoints):
                kp1_name = list(keypoints.keys())[connection[0]] if connection[0] < len(keypoints) else None
                kp2_name = list(keypoints.keys())[connection[1]] if connection[1] < len(keypoints) else None
                
                if kp1_name and kp2_name and kp1_name in keypoints and kp2_name in keypoints:
                    kp1 = keypoints[kp1_name]
                    kp2 = keypoints[kp2_name]
                    
                    if kp1['confidence'] > 0.3 and kp2['confidence'] > 0.3:
                        cv2.line(output, 
                                (int(kp1['x']), int(kp1['y'])),
                                (int(kp2['x']), int(kp2['y'])),
                                (0, 255, 0), 2)
        
        # Draw keypoints
        for name, kp in keypoints.items():
            if kp['confidence'] > 0.3:
                cv2.circle(output, (int(kp['x']), int(kp['y'])), 5, (0, 0, 255), -1)
        
        # Draw person ID and tracking confidence
        if 'hip_center' in keypoints:
            center = keypoints['hip_center']
            cv2.putText(output, f"ID: {person['person_id']}", 
                       (int(center['x']), int(center['y']) - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        # Display some angles
        y_offset = 30
        angles_to_show = ['right_knee', 'left_knee', 'right_elbow', 'left_elbow']
        
        for angle_name in angles_to_show:
            if angle_name in person['angles']['joint_angles']:
                angle_value = person['angles']['joint_angles'][angle_name]
                if angle_value is not None:
                    cv2.putText(output, f"{angle_name}: {angle_value:.1f}°",
                               (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    y_offset += 20
    
    # Display frame metrics
    metrics = result['frame_metrics']
    cv2.putText(output, f"Persons: {metrics['detected_persons']}", 
               (10, output.shape[0] - 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(output, f"FPS: {metrics['processing_fps']:.1f}", 
               (10, output.shape[0] - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return output

def process_video(video_path):
    """Process video and display results"""
    cap = cv2.VideoCapture(video_path)
    processor = FrameProcessor()
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    processor.set_fps(fps)
    
    print(f"Processing video: {video_path}")
    print(f"FPS: {fps}")
    
    cv2.namedWindow('Pose Analysis Demo', cv2.WINDOW_NORMAL)
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        result = processor.process_frame(frame, frame_count / fps)
        
        # Visualize
        output_frame = visualize_frame(frame, result)
        
        # Display
        cv2.imshow('Pose Analysis Demo', output_frame)
        
        # Save some statistics
        if frame_count % 30 == 0:  # Every second
            print(f"\nFrame {frame_count}:")
            print(f"  Detected persons: {result['frame_metrics']['detected_persons']}")
            print(f"  Processing time: {result['processing_time_ms']:.1f}ms")
            
            for person in result['persons']:
                print(f"  Person {person['person_id']}:")
                print(f"    Height: {person['metrics']['height_pixels']:.1f}px")
                print(f"    Visible side: {person['metrics']['visible_side']}")
        
        frame_count += 1
        
        # Exit on 'q' or ESC
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nProcessed {frame_count} frames")

def process_webcam():
    """Process webcam feed in real-time"""
    cap = cv2.VideoCapture(0)
    processor = FrameProcessor()
    
    print("Starting webcam analysis...")
    print("Press 'q' or ESC to quit")
    
    cv2.namedWindow('Webcam Pose Analysis', cv2.WINDOW_NORMAL)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        result = processor.process_frame(frame)
        
        # Visualize
        output_frame = visualize_frame(frame, result)
        
        # Display
        cv2.imshow('Webcam Pose Analysis', output_frame)
        
        frame_count += 1
        
        # Exit on 'q' or ESC
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

def plot_angle_timeseries(results):
    """Plot angle data over time"""
    # Extract time series data
    timestamps = [r['timestamp'] for r in results]
    
    # Get angle data for first person
    if results and results[0]['persons']:
        person_id = results[0]['persons'][0]['person_id']
        
        angles_data = {}
        for result in results:
            for person in result['persons']:
                if person['person_id'] == person_id:
                    for angle_name, value in person['angles']['joint_angles'].items():
                        if angle_name not in angles_data:
                            angles_data[angle_name] = []
                        angles_data[angle_name].append(value)
        
        # Plot
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()
        
        angles_to_plot = ['right_knee', 'left_knee', 'right_hip', 'left_hip']
        
        for i, angle_name in enumerate(angles_to_plot):
            if angle_name in angles_data and i < len(axes):
                ax = axes[i]
                values = angles_data[angle_name]
                
                # Filter out None values
                valid_indices = [j for j, v in enumerate(values) if v is not None]
                valid_timestamps = [timestamps[j] for j in valid_indices]
                valid_values = [values[j] for j in valid_indices]
                
                ax.plot(valid_timestamps, valid_values)
                ax.set_title(angle_name.replace('_', ' ').title())
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Angle (degrees)')
                ax.grid(True)
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Pose Analysis Demo')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--webcam', action='store_true', help='Use webcam')
    parser.add_argument('--plot', action='store_true', help='Plot angle timeseries')
    
    args = parser.parse_args()
    
    if args.webcam:
        process_webcam()
    elif args.video:
        if args.plot:
            # Process entire video and plot results
            from src.processing.video_processor import VideoProcessor
            processor = VideoProcessor()
            results = processor._process_video_sync(
                args.video, None, None, 1, False, 'none'
            )
            plot_angle_timeseries(results['results'])
        else:
            process_video(args.video)
    else:
        print("Please specify --video <path> or --webcam")
        print("\nExamples:")
        print("  python demo_video.py --webcam")
        print("  python demo_video.py --video sample.mp4")
        print("  python demo_video.py --video sample.mp4 --plot")