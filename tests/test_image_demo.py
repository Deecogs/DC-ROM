# test_image_demo.py
import cv2
from test_client import ROMCalculatorClient
def test_with_image(image_path):
    client = ROMCalculatorClient()
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return
        
    try:
        # Process image
        result = client.process_frame(image)
        
        # Display results
        print("ROM Results:")
        print(f"Angles: {result['angles']}")
        print(f"Joint Positions: {result['joint_positions']}")
        
        # Display images
        cv2.imshow('Original', image)
        if 'processed_frame' in result:
            cv2.imshow('Processed', result['processed_frame'])
            cv2.waitKey(0)
            
    except Exception as e:
        print(f"Error processing image: {e}")
        
    finally:
        cv2.destroyAllWindows()