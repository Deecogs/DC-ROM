"""
Test Pose Analyzer API with an actual image file
"""

import requests
import json
import sys
from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"

def download_sample_image():
    """Download a sample image with a person"""
    import urllib.request
    
    # Using a sample image URL (person doing yoga/exercise)
    sample_urls = [
        "https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/master/examples/media/COCO_val2014_000000000192.jpg",
        "https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/master/examples/media/COCO_val2014_000000000241.jpg"
    ]
    
    for i, url in enumerate(sample_urls):
        try:
            filename = f"sample_person_{i+1}.jpg"
            print(f"Downloading sample image {i+1}...")
            urllib.request.urlretrieve(url, filename)
            print(f"  ✓ Downloaded: {filename}")
            return filename
        except Exception as e:
            print(f"  ✗ Failed to download from {url}: {e}")
    
    return None

def analyze_image(image_path):
    """Analyze an image using the API"""
    print(f"\nAnalyzing: {image_path}")
    
    if not Path(image_path).exists():
        print(f"  ✗ File not found: {image_path}")
        return None
    
    # Read and display image info
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    print(f"  Image size: {width}x{height}")
    
    # Send to API
    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/jpeg")}
        response = requests.post(f"{API_URL}/api/analyze/image", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ Analysis successful!")
        print(f"  - Processing time: {result['processing_time_ms']:.2f}ms")
        print(f"  - Detected persons: {result['frame_metrics']['detected_persons']}")
        
        # Show details for each person
        for person in result['persons']:
            print(f"\n  Person {person['person_id']}:")
            print(f"    - Tracking confidence: {person['tracking_confidence']:.2f}")
            
            # Keypoints
            keypoints = person['keypoints']
            visible_keypoints = sum(1 for kp in keypoints.values() if kp['confidence'] > 0.5)
            print(f"    - Visible keypoints: {visible_keypoints}/{len(keypoints)}")
            
            # Some key keypoints
            key_points = ['nose', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
            print("    - Key points:")
            for kp_name in key_points:
                if kp_name in keypoints:
                    kp = keypoints[kp_name]
                    if kp['confidence'] > 0.5:
                        print(f"      • {kp_name}: ({kp['x']:.1f}, {kp['y']:.1f}) conf={kp['confidence']:.2f}")
            
            # Angles
            joint_angles = person['angles']['joint_angles']
            print("    - Joint angles:")
            for angle_name, angle_value in joint_angles.items():
                if angle_value is not None:
                    print(f"      • {angle_name}: {angle_value:.1f}°")
            
            # Metrics
            metrics = person['metrics']
            print(f"    - Height: {metrics['height_pixels']:.1f} pixels")
            print(f"    - Visible side: {metrics['visible_side']}")
            print(f"    - Movement direction: {metrics['movement_direction']}")
        
        return result
    else:
        print(f"  ✗ Error {response.status_code}: {response.text}")
        return None

def visualize_results(image_path, results):
    """Visualize the pose detection results"""
    if not results or not results['persons']:
        print("\nNo persons detected to visualize")
        return
    
    print("\nVisualizing results...")
    
    # Read image
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # Original image
    ax1.imshow(img_rgb)
    ax1.set_title("Original Image")
    ax1.axis('off')
    
    # Image with pose overlay
    ax2.imshow(img_rgb)
    ax2.set_title("Detected Pose")
    ax2.axis('off')
    
    # Draw pose for each person
    colors = ['red', 'blue', 'green', 'yellow', 'purple']
    
    for person_idx, person in enumerate(results['persons']):
        color = colors[person_idx % len(colors)]
        keypoints = person['keypoints']
        
        # Draw keypoints
        for kp_name, kp in keypoints.items():
            if kp['confidence'] > 0.5:
                ax2.scatter(kp['x'], kp['y'], c=color, s=50, alpha=0.8)
                ax2.text(kp['x']+5, kp['y']+5, kp_name[:3], fontsize=8, color=color)
        
        # Draw connections (simplified skeleton)
        connections = [
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle')
        ]
        
        for start, end in connections:
            if start in keypoints and end in keypoints:
                if keypoints[start]['confidence'] > 0.5 and keypoints[end]['confidence'] > 0.5:
                    ax2.plot([keypoints[start]['x'], keypoints[end]['x']], 
                            [keypoints[start]['y'], keypoints[end]['y']], 
                            color=color, linewidth=2, alpha=0.6)
        
        # Add person info
        if 'hip_center' in keypoints:
            center = keypoints['hip_center']
            ax2.text(center['x'], center['y']-50, f"Person {person['person_id']}", 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.5),
                    fontsize=10, color='white', ha='center')
    
    plt.tight_layout()
    plt.savefig('pose_detection_result.png', dpi=150, bbox_inches='tight')
    print("  ✓ Visualization saved to: pose_detection_result.png")
    plt.show()

def main():
    print("="*60)
    print("Pose Analyzer API - Image Test")
    print("="*60)
    
    # Check if user provided an image path
    image_path = '/Users/chandansharma/Desktop/workspace/deecogs-workspace/pose-analyzer-api/script/test.png'
    # if len(sys.argv) > 1:
    #     image_path = sys.argv[1]
    #     print(f"Using provided image: {image_path}")
    # else:
    #     # Download sample image
    #     print("No image provided. Downloading sample image...")
    #     image_path = download_sample_image()
        
    #     if not image_path:
    #         print("\n✗ Could not download sample image.")
    #         print("\nUsage: python test_with_image.py <path_to_image>")
    #         print("Example: python test_with_image.py person.jpg")
    #         return
    
    # Analyze the image
    results = analyze_image(image_path)
    
    if results:
        # Save full results
        with open("full_api_response.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n✓ Full API response saved to: full_api_response.json")
        
        # Visualize results
        visualize_results(image_path, results)
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()