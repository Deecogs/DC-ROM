import os
from typing import List, Union
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # API Settings
    PORT: int = 8000
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:3001"
    MAX_UPLOAD_SIZE_MB: int = 100
    ENABLE_WEBSOCKET: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Pose Detection Settings
    POSE_MODEL: str = "mediapipe"  # mediapipe, rtmpose (future)
    CONFIDENCE_THRESHOLD: float = 0.5
    MIN_DETECTION_CONFIDENCE: float = 0.5
    MIN_TRACKING_CONFIDENCE: float = 0.5
    
    # Person Detection Settings
    MAX_NUM_PERSONS: int = 5
    PERSON_DETECTION_THRESHOLD: float = 0.3
    KEYPOINT_LIKELIHOOD_THRESHOLD: float = 0.3
    AVERAGE_LIKELIHOOD_THRESHOLD: float = 0.5
    KEYPOINT_NUMBER_THRESHOLD: float = 0.3
    
    # Processing Settings
    INTERPOLATE: bool = True
    INTERPOLATION_GAP_SIZE: int = 10
    FILTER_TYPE: str = "butterworth"  # butterworth, gaussian, median
    BUTTERWORTH_ORDER: int = 4
    BUTTERWORTH_CUTOFF: float = 6.0
    GAUSSIAN_SIGMA: float = 1.0
    MEDIAN_KERNEL_SIZE: int = 3
    
    # Angle Calculation Settings
    FLIP_LEFT_RIGHT: bool = True
    CALCULATE_JOINT_ANGLES: bool = True
    CALCULATE_SEGMENT_ANGLES: bool = True
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()