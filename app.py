import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import base64
import cv2
import numpy as np
from exercise_handler import ExerciseHandler  # Importing the ExerciseHandler class

app = FastAPI(
    title="ROM Calculator API with WebSocket",
    description="WebSocket API for Range of Motion calculations using pose estimation",
    version="1.0.0"
)

# HTML page for live demo
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROM Calculator - Hawkins Test</title>
</head>
<body>
    <h1>ROM Calculator - Hawkins Test</h1>
    <video id="video" autoplay playsinline style="border:1px solid black; width:640px; height:480px;"></video>
    <canvas id="canvas" style="border:1px solid black; width:640px; height:480px;"></canvas>
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const ws = new WebSocket('ws://localhost:8000/ws');

        async function initWebcam() {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        }

        video.addEventListener('play', () => {
            const fps = 10;
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

        ws.onmessage = (event) => {
            const image = new Image();
            image.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
            };
            image.src = event.data;
        };

        initWebcam();
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    exercise_handler = ExerciseHandler("hawkins")  # Initialize the exercise handler with "hawkins" or "lowerback" test
    while True:
        try:
            # Receive base64-encoded frame
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(",")[1])
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the frame using the selected exercise handler
            processed_frame, rom_data = exercise_handler.process_frame(frame)

            # Encode processed frame and send back
            _, buffer = cv2.imencode(".jpg", processed_frame)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            await websocket.send_text(f"data:image/jpeg;base64,{frame_b64}")

        except Exception as e:
            print(f"Error: {e}")
            break
    await websocket.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
