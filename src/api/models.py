from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class ProcessingMode(str, Enum):
    """Processing mode options"""
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"

class AnalysisRequest(BaseModel):
    """Request model for video/image analysis"""
    mode: ProcessingMode = ProcessingMode.BALANCED
    start_time: Optional[float] = Field(None, description="Start time in seconds")
    end_time: Optional[float] = Field(None, description="End time in seconds")
    return_visualization: bool = Field(False, description="Return annotated frames")

class KeypointData(BaseModel):
    """Single keypoint data"""
    x: float
    y: float
    confidence: float

class AngleData(BaseModel):
    """Angle measurements"""
    joint_angles: Dict[str, Optional[float]]
    segment_angles: Dict[str, Optional[float]]

class VelocityData(BaseModel):
    """Velocity data"""
    x: float
    y: float

class PersonMetrics(BaseModel):
    """Metrics for a person"""
    height_pixels: float
    center_of_mass: Dict[str, float]
    velocity: VelocityData
    visible_side: str
    movement_direction: str

class PersonData(BaseModel):
    """Data for a single person"""
    person_id: int
    tracking_confidence: float
    keypoints: Dict[str, KeypointData]
    angles: AngleData
    metrics: PersonMetrics

class FrameMetrics(BaseModel):
    """Frame-level metrics"""
    detected_persons: int
    average_confidence: float
    processing_fps: float

class FrameAnalysisResult(BaseModel):
    """Result for a single frame analysis"""
    frame_id: int
    timestamp: float
    processing_time_ms: float
    persons: List[PersonData]
    frame_metrics: FrameMetrics

class VideoAnalysisResult(BaseModel):
    """Result for video analysis"""
    total_frames: int
    fps: float
    duration: float
    frames: List[FrameAnalysisResult]

class AngleDefinition(BaseModel):
    """Definition of an angle calculation"""
    name: str
    points: List[str]
    type: str
    description: str

class AngleDefinitionsResponse(BaseModel):
    """Response containing angle definitions"""
    joint_angles: List[AngleDefinition]
    segment_angles: List[AngleDefinition]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model: str
    timestamp: float

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int