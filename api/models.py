# api/models.py
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np

class Frame(BaseModel):
    image_data: str  # Base64 encoded image
    test_type: str   # Type of ROM test to perform
    
    class Config:
        arbitrary_types_allowed = True

class ROMResult(BaseModel):
    angles: Dict[str, float]
    joint_positions: Dict[str, Dict[str, int]]
    processed_image: Optional[str] = None  # Base64 encoded processed image

class TestConfig(BaseModel):
    test_type: str
    include_visualization: bool = True
    save_results: bool = False