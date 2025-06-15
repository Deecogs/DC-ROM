"""
Test video analysis with Sports2D-style visualization
"""

import cv2
import numpy as np
import requests
import json
import sys
from pathlib import Path
import time
from tqdm import tqdm

# Add the src directory to path to import the visualizer
sys.path.append(str(Path(__file__).parent.parent))
from src.visualization.sports2d_drawer import Sports2DVisualizer

API_URL = "http://localhost:8000"

def analyze_video_with_api(video_path, output_path="output_with_pose.mp4", skip_frames=1, 
                          save_json=True, display_angle_values_on=['body', 'list']):
    """
    Analyze video using the API and create output video with Sports2D-style visualization
    
    Args:
        video_path: Path to input video
        output_path: Path to save output video
        skip_frames: Process every Nth frame (1 = process all frames)
        save_json: Whether to save JSON responses
        display_angle_values_on: Where to display angles ['body', 'list', 'none']
    """
    
    print(f"\n{'='*60}")
    print(f"Video Analysis with Sports2D Visualization")
    print(f"{'='*60}")
    print(f"Input video: {video_path}")
    print(f"Output video: {output_path}")
    print(f"Skip frames: {skip_frames}")
    print(f"Display angles on: {display_angle_values_on}")
    print()
    
    # Initialize visualizer
    visualizer = Sports2DVisualizer()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video properties:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {total_frames}")
    print(f"  - Duration: {total_frames/fps:.2f} seconds")
    print()
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Process frames
    frame_count = 0
    processed_frames = 0
    all_results = []
    
    print("Processing frames...")
    pbar = tqdm(total=total_frames)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame based on skip_frames
        if frame_count % skip_frames == 0:
            # Convert frame to JPEG bytes
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = img_encoded.tobytes()
            
            # Send to API
            try:
                files = {"file": ("frame.jpg", img_bytes, "image/jpeg")}
                response = requests.post(f"{API_URL}/api/analyze/image", files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Add frame number to result
                    result['video_frame_number'] = frame_count
                    result['video_timestamp'] = frame_count / fps
                    
                    # Store result
                    all_results.append(result)
                    
                    # Draw using Sports2D visualizer
                    try:
                        frame_with_annotations = visualizer.draw_frame(
                            frame.copy(), result, display_angle_values_on
                        )
                    except Exception as viz_error:
                        print(f"Visualization error on frame {frame_count}: {viz_error}")
                        # Fall back to original frame
                        frame_with_annotations = frame.copy()
                        cv2.putText(frame_with_annotations, f"Viz Error: {str(viz_error)[:50]}", 
                                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Add frame info overlay
                    add_frame_info(frame_with_annotations, result)
                    
                    # Write frame
                    out.write(frame_with_annotations)
                    processed_frames += 1
                    
                    # Print first few frames' JSON
                    if processed_frames <= 2:
                        print(f"\n{'='*40}")
                        print(f"Frame {frame_count} JSON Response:")
                        print(f"{'='*40}")
                        print_abbreviated_json(result)
                        print(f"{'='*40}\n")
                    
                else:
                    print(f"Error processing frame {frame_count}: {response.status_code}")
                    out.write(frame)
                    
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                out.write(frame)
        else:
            # Write original frame
            out.write(frame)
        
        frame_count += 1
        pbar.update(1)
    
    pbar.close()
    
    # Release everything
    cap.release()
    out.release()
    
    print(f"\nProcessing complete!")
    print(f"  - Frames processed: {processed_frames}/{total_frames}")
    print(f"  - Output video saved: {output_path}")
    
    # Save all JSON results
    if save_json and all_results:
        json_output_path = Path(output_path).stem + "_analysis.json"
        with open(json_output_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"  - JSON results saved: {json_output_path}")
        
        # Print summary statistics
        print_analysis_summary(all_results)
    
    return all_results

def add_frame_info(frame, result):
    """Add frame information overlay"""
    # Create semi-transparent overlay for info
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 40), (0, 0, 0), -1)
    frame[:40] = cv2.addWeighted(overlay[:40], 0.7, frame[:40], 0.3, 0)
    
    # Add text
    info_text = f"Frame: {result.get('video_frame_number', 0)} | Time: {result.get('video_timestamp', 0):.2f}s | Persons: {result['frame_metrics']['detected_persons']} | FPS: {result['frame_metrics']['processing_fps']:.1f}"
    cv2.putText(frame, info_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

def print_abbreviated_json(result):
    """Print abbreviated JSON response focusing on key information"""
    print(f"Timestamp: {result.get('video_timestamp', 0):.2f}s")
    print(f"Processing time: {result['processing_time_ms']:.2f}ms")
    print(f"Detected persons: {result['frame_metrics']['detected_persons']}")
    
    for person in result['persons'][:2]:  # Show max 2 persons
        print(f"\nPerson {person['person_id']}:")
        print(f"  Tracking confidence: {person['tracking_confidence']:.2f}")
        
        # Show all joint angles
        print("  Joint angles:")
        for name, value in person['angles']['joint_angles'].items():
            if value is not None:
                print(f"    {name}: {value:.1f}°")
        
        # Show all segment angles
        print("  Segment angles:")
        for name, value in person['angles']['segment_angles'].items():
            if value is not None:
                print(f"    {name}: {value:.1f}°")
        
        # Show metrics
        metrics = person['metrics']
        print(f"  Height: {metrics['height_pixels']:.1f} pixels")
        print(f"  Visible side: {metrics['visible_side']}")

def print_analysis_summary(results):
    """Print summary statistics from all frames"""
    print(f"\n{'='*60}")
    print("Analysis Summary")
    print(f"{'='*60}")
    
    # Total persons detected across all frames
    total_detections = sum(r['frame_metrics']['detected_persons'] for r in results)
    avg_persons = total_detections / len(results) if results else 0
    
    print(f"Total frames analyzed: {len(results)}")
    print(f"Average persons per frame: {avg_persons:.2f}")
    
    # Collect all unique person IDs and angle statistics
    all_person_ids = set()
    angle_stats = {}
    
    for r in results:
        for p in r['persons']:
            all_person_ids.add(p['person_id'])
            
            # Collect angle statistics
            for angle_type in ['joint_angles', 'segment_angles']:
                for angle_name, angle_value in p['angles'][angle_type].items():
                    if angle_value is not None:
                        if angle_name not in angle_stats:
                            angle_stats[angle_name] = []
                        angle_stats[angle_name].append(angle_value)
    
    print(f"Unique persons tracked: {len(all_person_ids)}")
    
    # Average processing time
    avg_processing_time = sum(r['processing_time_ms'] for r in results) / len(results) if results else 0
    print(f"Average processing time: {avg_processing_time:.2f}ms per frame")
    print(f"Average FPS: {1000/avg_processing_time:.1f}")
    
    # Angle statistics
    if angle_stats:
        print("\nAngle Statistics (across all frames):")
        
        # Joint angles
        print("\nJoint Angles:")
        joint_angles = ['right_ankle', 'left_ankle', 'right_knee', 'left_knee', 
                       'right_hip', 'left_hip', 'right_shoulder', 'left_shoulder',
                       'right_elbow', 'left_elbow']
        
        for angle_name in joint_angles:
            if angle_name in angle_stats:
                values = angle_stats[angle_name]
                print(f"  {angle_name}:")
                print(f"    - Mean: {np.mean(values):.1f}° (±{np.std(values):.1f}°)")
                print(f"    - Range: [{np.min(values):.1f}°, {np.max(values):.1f}°]")
        
        # Segment angles
        print("\nSegment Angles:")
        segment_angles = ['right_foot', 'left_foot', 'right_shank', 'left_shank',
                         'right_thigh', 'left_thigh', 'trunk', 'right_arm', 'left_arm',
                         'right_forearm', 'left_forearm']
        
        for angle_name in segment_angles:
            if angle_name in angle_stats:
                values = angle_stats[angle_name]
                print(f"  {angle_name}:")
                print(f"    - Mean: {np.mean(values):.1f}° (±{np.std(values):.1f}°)")
                print(f"    - Range: [{np.min(values):.1f}°, {np.max(values):.1f}°]")
    
    print(f"{'='*60}\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Video Analysis with Sports2D-style visualization')
    parser.add_argument('video_path', help='Path to input video')
    parser.add_argument('-o', '--output', default='output_with_pose.mp4', help='Output video path')
    parser.add_argument('-s', '--skip', type=int, default=1, help='Process every Nth frame')
    parser.add_argument('--display', nargs='*', default=['body', 'list'], 
                       choices=['body', 'list', 'none'], 
                       help='Where to display angles')
    parser.add_argument('--no-json', action='store_true', help='Do not save JSON output')
    
    args = parser.parse_args()
    
    # Check if video exists
    if not Path(args.video_path).exists():
        print(f"Error: Video file not found: {args.video_path}")
        sys.exit(1)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("Error: API is not responding correctly")
            sys.exit(1)
    except:
        print(f"Error: Cannot connect to API at {API_URL}")
        print("Make sure the API is running: python -m src.main")
        sys.exit(1)
    
    # Analyze video
    analyze_video_with_api(
        args.video_path, 
        args.output, 
        args.skip,
        save_json=not args.no_json,
        display_angle_values_on=args.display
    )

if __name__ == "__main__":
    main()