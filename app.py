import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import base64
import cv2
import numpy as np
import json
from exercise_handler import ExerciseHandler
import httpx  # For HTTP requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ROM Calculator API with WebSocket",
    description="WebSocket API for Range of Motion calculations using pose estimation",
    version="1.0.0"
)

# Allow all origins, methods, and headers (for development)
# Allow CORS for all origins, methods, and headers (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROM Calculator - Exercise Test</title>
    <style>
        .container {
            display: flex;
            gap: 20px;
            padding: 20px;
        }
        .video-container {
            flex: 1;
        }
        .data-container {
            flex: 1;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 8px;
            max-width: 400px;
        }
        .rom-data {
            font-family: monospace;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h1>ROM Calculator - Exercise Test</h1>
    <div class="container">
        <div class="video-container">
            <video id="video" autoplay playsinline style="border:1px solid black; width:640px; height:480px;"></video>
            <canvas id="canvas" style="border:1px solid black; width:640px; height:480px;"></canvas>
        </div>
        <div class="data-container">
            <h2>ROM Data</h2>
            <pre id="romData" class="rom-data">Waiting for data...</pre>
        </div>
    </div>
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const romDataElement = document.getElementById('romData');
        const ctx = canvas.getContext('2d');
        const ws = new WebSocket('ws://localhost:8000/process_frame');

        async function initWebcam() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
            } catch (err) {
                console.error('Error accessing webcam:', err);
            }
        }

        video.addEventListener('play', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
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
            const data = JSON.parse(event.data);
            const image = new Image();
            image.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
            };
            image.src = data.image;
            romDataElement.textContent = JSON.stringify(data.rom_data, null, 2);
        };

        ws.onerror = (error) => console.error('WebSocket error:', error);
        ws.onclose = () => console.log('WebSocket connection closed');

        initWebcam();
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html_content)


@app.get("/test")
async def get_data():
    return {"message": "Success"}

@app.websocket("/process_frame")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    exercise_handler = ExerciseHandler("lowerback")
    llm_api_url = "http://llm-api-endpoint/rom"  # Replace with actual URL

    async with httpx.AsyncClient() as client:
        try:
            while True:
                data = await websocket.receive_text()
                image_data = base64.b64decode(data.split(",")[1])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                processed_frame, rom_data = exercise_handler.process_frame(frame)

                _, buffer = cv2.imencode(".jpg", processed_frame)
                frame_b64 = base64.b64encode(buffer).decode("utf-8")

                llm_result = {"info": "LLM API is unavailable; only ROM data processed"}
                try:
                    llm_response = await client.post(llm_api_url, json={"rom_data": rom_data})
                    if llm_response.status_code == 200:
                        llm_result = llm_response.json()
                except httpx.RequestError as e:
                    print(f"LLM API Request Error: {e}")
                except Exception as e:
                    print(f"Unexpected LLM API error: {e}")

                response_data = {
                    "image": f"NULL",
                    "rom_data": rom_data,
                    "llm_result": llm_result
                }
                await websocket.send_text(json.dumps(response_data))
        except Exception as e:
            print(f"WebSocket Error: {e}")
        finally:
            if websocket.client_state.CONNECTED:
                await websocket.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
