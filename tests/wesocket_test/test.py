import base64
import cv2
import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Load a test image
        image = cv2.imread("test-image.jpg")
        _, buffer = cv2.imencode(".jpg", image)
        image_data = base64.b64encode(buffer).decode("utf-8")
        await websocket.send(f"data:image/jpeg;base64,{image_data}")
        
        # Receive and print landmarks
        response = await websocket.recv()
        print(response)

asyncio.run(test_websocket())
