# client_demo.py
import cv2
from test_client import ROMCalculatorClient
def run_client_demo():
    # Initialize client
    client = ROMCalculatorClient()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
            
        try:
            # Process frame
            result = client.process_frame(frame)
            
            # Display original and processed frames
            cv2.imshow('Original', frame)
            if 'processed_frame' in result:
                cv2.imshow('Processed', result['processed_frame'])
                
            # Display angles
            print(f"Angles: {result['angles']}")
            
        except Exception as e:
            print(f"Error: {e}")
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_client_demo()