#!/usr/bin/env python3
"""
MediaPipe Holistic ROM Analysis Demo
-----------------------------------
This script demonstrates real-time lower back ROM analysis using the MediaPipe Holistic model.
It provides a comprehensive view of face, body, and hand tracking with ROM measurements.

Usage:
    python holistic_demo.py [--source 0] [--output output.mp4]

Arguments:
    --source: Camera index or video file path (default: 0)
    --output: Optional output video file
    --complexity: Model complexity (0, 1, or 2) (default: 1)
"""

import cv2
import numpy as np
import argparse
import time
import os
import logging
from utils.pose_detector import PoseDetector
from utils.visualization import PoseVisualizer
from rom.lower_back_test import LowerBackFlexionTest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("holistic_demo")

def parse_args():
    parser = argparse.ArgumentParser(description="Holistic ROM Analysis Demo")
    parser.add_argument('--source', type=str, default='0', 
                        help='Camera index or video file (default: 0)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output video file path (optional)')
    parser.add_argument('--complexity', type=int, default=1, choices=[0, 1, 2],
                        help='Model complexity (0, 1, or 2) (default: 1)')
    parser.add_argument('--width', type=int, default=1280,
                        help='Output width (default: 1280)')
    parser.add_argument('--height', type=int, default=720,
                        help='Output height (default: 720)')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Determine source (camera or video file)
    if args.source.isdigit():
        source = int(args.source)
    else:
        source = args.source
        if not os.path.exists(source):
            logger.error(f"Error: Source file '{source}' not found")
            return
    
    # Initialize components
    logger.info(f"Initializing Holistic model with complexity {args.complexity}")
    pose_detector = PoseDetector(
        model_complexity=args.complexity,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    visualizer = PoseVisualizer()
    lower_back_test = LowerBackFlexionTest(pose_detector, visualizer)
    
    # Initialize video capture
    logger.info(f"Opening video source: {source}")
    cap = cv2.VideoCapture(source)
    
    # Try to set camera resolution if using webcam
    if isinstance(source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    
    if not cap.isOpened():
        logger.error(f"Error: Could not open video source {source}")
        return
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize video writer if output file specified
    video_writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            args.output, fourcc, fps, (frame_width, frame_height))
        logger.info(f"Recording output to: {args.output}")
    
    # Variables for ROM tracking
    rom_values = {
        'min_angle': 180,
        'max_angle': 0,
        'current_angle': 0
    }
    
    # Create display window
    window_name = "Holistic ROM Analysis"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    # Main processing loop
    frame_count = 0
    start_time = time.time()
    processing_times = []
    
    logger.info("Starting ROM analysis. Press 'q' to quit, 'r' to reset ROM measurements.")
    
    while True:
        # Read frame from video source
        ret, frame = cap.read()
        if not ret:
            if source != 0:  # If it's a video file and we've reached the end
                logger.info("End of video file reached")
                break
            logger.warning("Error: Could not read frame")
            continue
        
        # Process frame
        frame_count += 1
        
        # Skip frames for performance if needed
        if frame_count % 1 != 0:  # Process every frame
            continue
        
        # Start timing for performance measurement
        process_start = time.time()
        
        try:
            # Get full body results from holistic model
            holistic_results = pose_detector.get_full_body_results(frame)
            
            # Use the annotated frame for further processing
            processed_frame = holistic_results['annotated_frame']
            
            # Process ROM with lower back test
            rom_frame, rom_data = lower_back_test.process_frame(frame)
            
            # Extract ROM indicators from lower back test
            if 'trunk_angle' in rom_data:
                rom_values['current_angle'] = rom_data['trunk_angle']
            
            if 'ROM' in rom_data and rom_data['ROM']:
                rom_values['min_angle'] = rom_data['ROM'][0]
                rom_values['max_angle'] = rom_data['ROM'][1]
            
            # Calculate processing time
            process_end = time.time()
            process_time = process_end - process_start
            processing_times.append(process_time)
            
            # Calculate average FPS
            avg_process_time = sum(processing_times[-30:]) / min(len(processing_times), 30)
            fps_text = f"FPS: {1/avg_process_time:.1f}" if avg_process_time > 0 else "FPS: N/A"
            
            # Add ROM overlay to the frame
            overlay = np.zeros((240, frame_width, 3), dtype=np.uint8)
            
            # Add text information
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(overlay, f"Current Angle: {rom_values['current_angle']:.1f}°", 
                      (20, 40), font, 0.8, (255, 255, 255), 2)
            cv2.putText(overlay, f"Min Angle: {rom_values['min_angle']:.1f}°", 
                      (20, 80), font, 0.8, (255, 255, 255), 2)
            cv2.putText(overlay, f"Max Angle: {rom_values['max_angle']:.1f}°", 
                      (20, 120), font, 0.8, (255, 255, 255), 2)
            cv2.putText(overlay, f"ROM Range: {rom_values['max_angle'] - rom_values['min_angle']:.1f}°", 
                      (20, 160), font, 0.8, (255, 255, 255), 2)
            cv2.putText(overlay, fps_text, 
                      (20, 200), font, 0.8, (255, 255, 255), 2)
            
            # Add status indicator
            status_text = "READY" if rom_data.get('is_ready', False) else "NOT READY"
            status_color = (0, 255, 0) if rom_data.get('is_ready', False) else (0, 0, 255)
            cv2.putText(overlay, status_text, 
                      (frame_width - 150, 40), font, 0.8, status_color, 2)
            
            # Add ROM gauge
            gauge_width = 400
            gauge_height = 30
            gauge_x = frame_width - gauge_width - 20
            gauge_y = 80
            
            # Draw gauge background
            cv2.rectangle(overlay, (gauge_x, gauge_y), 
                        (gauge_x + gauge_width, gauge_y + gauge_height), 
                        (100, 100, 100), -1)
            
            # Draw gauge fill based on current angle
            angle_percentage = min(rom_values['current_angle'] / 180.0, 1.0)
            fill_width = int(gauge_width * angle_percentage)
            
            # Color gradient from green to red
            if angle_percentage < 0.5:
                color = (0, 255, int(255 * angle_percentage * 2))
            else:
                color = (0, int(255 * (1 - angle_percentage) * 2), 255)
                
            cv2.rectangle(overlay, (gauge_x, gauge_y), 
                        (gauge_x + fill_width, gauge_y + gauge_height), 
                        color, -1)
            
            # Add gauge markers
            for i in range(5):
                marker_x = gauge_x + (gauge_width * i // 4)
                cv2.line(overlay, (marker_x, gauge_y), 
                       (marker_x, gauge_y + gauge_height), (200, 200, 200), 1)
                cv2.putText(overlay, f"{i * 45}°", 
                          (marker_x - 15, gauge_y + gauge_height + 20), 
                          font, 0.5, (200, 200, 200), 1)
            
            # Add guidance message
            if 'guidance' in rom_data:
                guidance_y = 120
                cv2.rectangle(overlay, (gauge_x, guidance_y), 
                            (gauge_x + gauge_width, guidance_y + 60), 
                            (50, 50, 50), -1)
                
                # Split guidance text to fit
                guidance_text = rom_data['guidance']
                words = guidance_text.split()
                line1 = ""
                line2 = ""
                
                for word in words:
                    if len(line1) + len(word) < 40:
                        line1 += word + " "
                    else:
                        line2 += word + " "
                
                cv2.putText(overlay, line1, 
                          (gauge_x + 5, guidance_y + 25), 
                          font, 0.5, (255, 255, 255), 1)
                
                if line2:
                    cv2.putText(overlay, line2, 
                              (gauge_x + 5, guidance_y + 50), 
                              font, 0.5, (255, 255, 255), 1)
            
            # Combine the overlay with the frame
            combined_height = frame_height + overlay.shape[0]
            combined_frame = np.zeros((combined_height, frame_width, 3), dtype=np.uint8)
            combined_frame[:frame_height, :] = processed_frame
            combined_frame[frame_height:, :] = overlay
            
            # Display the frame
            cv2.imshow(window_name, combined_frame)
            
            # Write to output video if specified
            if video_writer:
                video_writer.write(combined_frame)
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            cv2.imshow(window_name, frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            logger.info("Quitting...")
            break
        elif key == ord('r'):
            logger.info("Resetting ROM measurements")
            rom_values['min_angle'] = 180
            rom_values['max_angle'] = 0
            lower_back_test.min_angle = 180
            lower_back_test.max_angle = 0
            lower_back_test.angle_buffer.clear()
    
    # Clean up
    cap.release()
    if video_writer:
        video_writer.release()
    cv2.destroyAllWindows()
    
    # Print final stats
    elapsed_time = time.time() - start_time
    logger.info(f"Processed {frame_count} frames in {elapsed_time:.2f} seconds")
    
    if rom_values['max_angle'] > rom_values['min_angle']:
        rom_range = rom_values['max_angle'] - rom_values['min_angle']
        logger.info(f"Final ROM range: {rom_range:.1f}°")
        logger.info(f"Min angle: {rom_values['min_angle']:.1f}°, Max angle: {rom_values['max_angle']:.1f}°")
    
    # Print average processing time
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        logger.info(f"Average processing time per frame: {avg_time*1000:.2f} ms ({1/avg_time:.1f} FPS)")

if __name__ == "__main__":
    main()