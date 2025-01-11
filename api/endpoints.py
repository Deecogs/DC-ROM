# api/endpoints.py
from fastapi import APIRouter, HTTPException
from .models import Frame, ROMResult, TestConfig
from .service import ROMService
from typing import List

router = APIRouter()
rom_service = ROMService()

@router.post("/process-frame/", response_model=ROMResult)
async def process_frame(frame: Frame):
    try:
        rom_data, processed_image = rom_service.process_frame(
            frame.image_data,
            frame.test_type
        )
        
        if not rom_data:
            raise HTTPException(status_code=400, detail="No pose detected in image")
            
        return ROMResult(
            angles={
                'horizontal': rom_data['angle'],
                'vertical': rom_data['vertical_angle']
            },
            joint_positions={
                'shoulder': {'x': rom_data['shoulder'][0], 'y': rom_data['shoulder'][1]},
                'elbow': {'x': rom_data['elbow'][0], 'y': rom_data['elbow'][1]},
                'wrist': {'x': rom_data['wrist'][0], 'y': rom_data['wrist'][1]}
            },
            processed_image=processed_image
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-roms/", response_model=List[str])
async def get_available_roms():
    return list(rom_service.test_types.keys())

@router.post("/configure-test/")
async def configure_test(config: TestConfig):
    if config.test_type not in rom_service.test_types:
        raise HTTPException(status_code=400, detail=f"Unsupported test type: {config.test_type}")
    return {"status": "success", "message": "Test configured successfully"}