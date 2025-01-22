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
mp_drawing = mp.solutions.drawing_utils  # To draw landmarks and connections

# Basic HTML for live demo
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pose Estimation Demo</title>
</head>
<body>
    <h1>MediaPipe Pose Estimation</h1>
    <video id="video" autoplay playsinline style="border:1px solid black; width:640px; height:480px;"></video>
    <canvas id="canvas" style="border:1px solid black; width:640px; height:480px;"></canvas>
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const ws = new WebSocket('ws://localhost:8000/ws');

        // Initialize webcam
        async function initWebcam() {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        }

        // Send frames to server
        video.addEventListener('play', () => {
            const fps = 10; // Limit frames per second
            setInterval(() => {
                const canvasTmp = document.createElement('canvas');
                canvasTmp.width = video.videoWidth;
                canvasTmp.height = video.videoHeight;
                const ctxTmp = canvasTmp.getContext('2d');
                ctxTmp.drawImage(video, 0, 0, canvasTmp.width, canvasTmp.height);
                const frameData = canvasTmp.toDataURL('image/jpeg');
                ws.send(frameData);
            }, 1000 / fps);
        });

        // Receive processed frames
        ws.onmessage = (event) => {
            const image = new Image();
            image.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
            };
            image.src = event.data;
        };

        // Initialize
        initWebcam();
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Receive the base64-encoded frame from the client
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(",")[1])
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame with MediaPipe
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Draw landmarks on the frame
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

            # Encode the processed frame to base64
            _, buffer = cv2.imencode(".jpg", frame)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            await websocket.send_text(f"data:image/jpeg;base64,{frame_b64}")

        except Exception as e:
            print(f"Error: {e}")
            break
    await websocket.close()
