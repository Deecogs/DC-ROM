from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from src.api.routes import router as api_router
from src.api.websocket import WebSocketManager
from src.config.settings import get_settings

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Pose Analyzer API",
    description="Real-time pose detection and angle calculation API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
ws_manager = WebSocketManager()

# Include API routes
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Pose Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "analyze_video": "/api/analyze/video",
            "analyze_image": "/api/analyze/image",
            "stream": "/api/analyze/stream (WebSocket)",
            "angle_definitions": "/api/angles/definitions"
        }
    }

# WebSocket endpoint for real-time analysis
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            result = await ws_manager.process_frame(data)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        ws_manager.disconnect(websocket)

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )