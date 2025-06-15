from fastapi import WebSocket
import cv2
import numpy as np
import json
from typing import List
import asyncio

from src.processing.frame_processor import FrameProcessor

class WebSocketManager:
    """Manage WebSocket connections for real-time streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.frame_processors = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        # Create a dedicated processor for this connection
        self.frame_processors[id(websocket)] = FrameProcessor()
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        # Clean up processor
        if id(websocket) in self.frame_processors:
            del self.frame_processors[id(websocket)]
    
    async def process_frame(self, frame_data: bytes, websocket_id: int = None) -> dict:
        """Process incoming frame data"""
        try:
            # Decode image from bytes
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {"error": "Invalid frame data"}
            
            # Get processor for this connection
            processor = self.frame_processors.get(websocket_id)
            if not processor:
                processor = FrameProcessor()
            
            # Process frame
            result = processor.process_frame(frame)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection might be closed
                pass