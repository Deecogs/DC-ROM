from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import mediapipe as mp
import cv2
import numpy as np
import base64

app = FastAPI()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

@app.get("/")
async def get():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Pose Estimation</title>
    </head>
    <body>
        <h1>Pose Estimation WebSocket</h1>
        <video id="video" autoplay playsinline></video>
        <script>
        const video = document.getElementById('video');
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            video.srcObject = stream;
            const socket = new WebSocket('ws://localhost:8000/ws');
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            setInterval(() => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg');
                socket.send(imageData);
            }, 100);
        });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Receive the base64-encoded image
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(",")[1])
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame with MediaPipe
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Extract pose landmarks if available
            if results.pose_landmarks:
                landmarks = [
                    {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                    for lm in results.pose_landmarks.landmark
                ]
                await websocket.send_json({"landmarks": landmarks})
            else:
                await websocket.send_json({"landmarks": []})
        except Exception as e:
            print(f"Error: {e}")
            break
    await websocket.close()
