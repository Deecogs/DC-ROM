# api/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
import numpy as np

class Point(BaseModel):
    """Model for a 2D point"""
    x: int
    y: int
    
    class Config:
        schema_extra = {
            "example": {
                "x": 100,
                "y": 200
            }
        }

class Frame(BaseModel):
    """Model for a video frame to be processed"""
    image_data: str = Field(..., description="Base64 encoded image data")
    test_type: str = Field(..., description="Type of ROM test to perform")
    
    @validator('test_type')
    def validate_test_type(cls, v):
        valid_types = ['lowerback', 'lowerback_flexion']
        if v.lower() not in valid_types:
            raise ValueError(f"test_type must be one of {valid_types}")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "image_data": "base64_encoded_image_data_here",
                "test_type": "lowerback"
            }
        }

class ROMResult(BaseModel):
    """Model for ROM analysis result"""
    test_type: str = Field(..., description="Type of ROM test performed")
    angles: List[float] = Field(..., description="ROM angle measurements")
    joint_positions: Dict[str, Any] = Field(default={}, description="Joint positions detected")
    processed_image: Optional[str] = Field(None, description="Base64 encoded processed image")
    rom_data: Dict[str, Any] = Field(default={}, description="Complete ROM data")
    
    class Config:
        schema_extra = {
            "example": {
                "test_type": "lowerback",
                "angles": [45.5, 100.2],
                "joint_positions": {
                    "shoulder": {"x": 100, "y": 150},
                    "hip": {"x": 120, "y": 250},
                    "knee": {"x": 130, "y": 350}
                },
                "rom_data": {
                    "trunk_angle": 85.5,
                    "ROM": [45.5, 100.2],
                    "is_ready": True
                }
            }
        }

class TestConfig(BaseModel):
    """Model for configuring a ROM test"""
    test_type: str = Field(..., description="Type of ROM test to configure")
    window_size: int = Field(10, description="Size of the angle measurement window")
    include_visualization: bool = Field(True, description="Include visualization in results")
    save_results: bool = Field(False, description="Save results to file")
    
    @validator('window_size')
    def validate_window_size(cls, v):
        if v < 3 or v > 50:
            raise ValueError("window_size must be between 3 and 50")
        return v
    
    @validator('test_type')
    def validate_test_type(cls, v):
        valid_types = ['lowerback', 'lowerback_flexion']
        if v.lower() not in valid_types:
            raise ValueError(f"test_type must be one of {valid_types}")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "test_type": "lowerback",
                "window_size": 10,
                "include_visualization": True,
                "save_results": False
            }
        }

class ErrorResponse(BaseModel):
    """Model for error responses"""
    detail: str = Field(..., description="Error detail message")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Error processing frame: No pose detected"
            }
        }