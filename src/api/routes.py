from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import time
import tempfile
import os
from typing import Optional

from src.api.models import (
    AnalysisRequest,
    FrameAnalysisResult,
    VideoAnalysisResult,
    AngleDefinitionsResponse,
    AngleDefinition,
    HealthResponse,
    ErrorResponse
)
from src.processing.frame_processor import FrameProcessor
from src.processing.video_processor import VideoProcessor
from src.utils.angle_definitions import JOINT_ANGLES, SEGMENT_ANGLES
from src.config.settings import get_settings

router = APIRouter()
settings = get_settings()

# Initialize processors
frame_processor = FrameProcessor()
video_processor = VideoProcessor()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model=settings.POSE_MODEL,
        timestamp=time.time()
    )

@router.post("/analyze/image", response_model=FrameAnalysisResult)
async def analyze_image(
    file: UploadFile = File(...)
):
    """Analyze a single image for pose and angles"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Process frame
        result = frame_processor.process_frame(image)
        
        return FrameAnalysisResult(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/video")
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    skip_frames: int = 1
):
    """
    Analyze a video file for pose and angles.
    Returns a job ID for checking status.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_path = tmp_file.name
        
        # Process video (this could be moved to a background task)
        results = await process_video_file(
            tmp_path,
            start_time=start_time,
            end_time=end_time,
            skip_frames=skip_frames
        )
        
        # Clean up
        os.unlink(tmp_path)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_file(
    video_path: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    skip_frames: int = 1
) -> VideoAnalysisResult:
    """Process a video file and return results"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # Set up frame processor
    processor = FrameProcessor()
    processor.set_fps(fps)
    
    # Calculate frame range
    start_frame = int(start_time * fps) if start_time else 0
    end_frame = int(end_time * fps) if end_time else total_frames
    
    # Process frames
    results = []
    frame_count = 0
    
    # Set start position
    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    while cap.isOpened() and frame_count < (end_frame - start_frame):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames if requested
        if frame_count % skip_frames == 0:
            timestamp = (start_frame + frame_count) / fps
            result = processor.process_frame(frame, timestamp)
            results.append(FrameAnalysisResult(**result))
        
        frame_count += 1
    
    cap.release()
    
    return VideoAnalysisResult(
        total_frames=len(results),
        fps=fps,
        duration=duration,
        frames=results
    )

@router.get("/angles/definitions", response_model=AngleDefinitionsResponse)
async def get_angle_definitions():
    """Get definitions of all calculated angles"""
    joint_angle_defs = []
    for name, definition in JOINT_ANGLES.items():
        joint_angle_defs.append(AngleDefinition(
            name=name,
            points=definition['points'],
            type=definition['type'],
            description=f"{name.replace('_', ' ').title()} - {definition['type']}"
        ))
    
    segment_angle_defs = []
    for name, definition in SEGMENT_ANGLES.items():
        segment_angle_defs.append(AngleDefinition(
            name=name,
            points=definition['points'],
            type=definition['type'],
            description=f"{name.replace('_', ' ').title()} angle with horizontal"
        ))
    
    return AngleDefinitionsResponse(
        joint_angles=joint_angle_defs,
        segment_angles=segment_angle_defs
    )

@router.post("/config")
async def update_config(config: dict):
    """Update processing configuration"""
    # This would update the settings dynamically
    # For now, return current config
    return {
        "message": "Configuration updated",
        "config": config
    }