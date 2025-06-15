# Create test_websocket.py
import asyncio
import websockets
import json
import cv2
import base64

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Open webcam
        cap = cv2.VideoCapture(0)
        
        for _ in range(10):  # Send 10 frames
            ret, frame = cap.read()
            if ret:
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                
                # Send to WebSocket
                await websocket.send(buffer.tobytes())
                
                # Receive result
                result = await websocket.recv()
                data = json.loads(result)
                print(f"Detected {data['frame_metrics']['detected_persons']} persons")
                
                await asyncio.sleep(0.1)
        
        cap.release()

# Run the test
asyncio.run(test_websocket())