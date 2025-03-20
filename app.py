import uvicorn
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import base64
import cv2
import numpy as np
import json
import time
from typing import Dict, Optional
from api.service import ROMService
from api.models import Frame, ROMResult, TestConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rom_api")

# Initialize FastAPI app
app = FastAPI(
    title="Range of Motion Analysis API",
    description="API for analyzing range of motion using pose estimation",
    version="1.0.0"
)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ROM service
rom_service = ROMService()

# Define connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
            
    async def send_response(self, client_id: str, response_data: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(response_data))
            
manager = ConnectionManager()

# Load HTML content for the demo page
with open("templates/index.html", "r") as file:
    html_content = file.read()

# Error handler middleware
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    return html_content

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ROM Analysis API",
        "version": "1.0.0"
    }

@app.get("/api/available-tests")
async def get_available_tests():
    tests = rom_service.get_available_tests()
    return {"available_tests": tests}

@app.post("/api/process-frame", response_model=ROMResult)
async def process_frame(frame: Frame):
    try:
        rom_data, processed_image = rom_service.process_frame(
            frame.image_data,
            frame.test_type
        )
        
        if "error" in rom_data:
            raise HTTPException(status_code=400, detail=rom_data["error"])
            
        return ROMResult(
            test_type=frame.test_type,
            angles=rom_data.get("ROM", [0, 0]),
            joint_positions=rom_data.get("joint_positions", {}),
            processed_image=processed_image,
            rom_data=rom_data
        )
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/configure-test")
async def configure_test(config: TestConfig):
    available_tests = rom_service.get_available_tests()
    if config.test_type not in available_tests:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported test type: {config.test_type}. Available tests: {available_tests}"
        )
    return {"status": "success", "message": "Test configured successfully"}

@app.websocket("/ws/process-frames/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, test_type: Optional[str] = "lowerback"):
    await manager.connect(websocket, client_id)
    
    try:
        # Send initial connection message
        await manager.send_response(
            client_id, 
            {
                "status": "connected",
                "message": f"Connected to ROM Analysis service",
                "test_type": test_type,
                "client_id": client_id
            }
        )
        
        while True:
            try:
                # Receive frame data
                data = await websocket.receive_text()
                
                if not data:
                    continue
                
                # Process frame
                rom_data, processed_frame = rom_service.process_frame(data, test_type)
                
                # Send response
                response_data = {
                    "image": f"data:image/jpeg;base64,{processed_frame}",
                    "rom_data": rom_data,
                    "timestamp": time.time()
                }
                await manager.send_response(client_id, response_data)
                
            except WebSocketDisconnect:
                manager.disconnect(client_id)
                break
                
            except Exception as e:
                logger.error(f"Error processing WebSocket frame: {str(e)}")
                await manager.send_response(
                    client_id,
                    {"status": "error", "error": str(e), "timestamp": time.time()}
                )
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        manager.disconnect(client_id)

# Mount static files (for the demo page)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    logger.warning("Static files directory not found. UI components may not load correctly.")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)