from typing import Dict
from src.models.base_model import BasePoseModel
from src.models.mediapipe_model import MediaPipeModel

class ModelFactory:
    """Factory class for creating pose estimation models"""
    
    _models = {
        'mediapipe': MediaPipeModel,
        # Future models can be added here
        # 'rtmpose': RTMPoseModel,
        # 'openpose': OpenPoseModel,
    }
    
    @classmethod
    def create_model(cls, model_name: str, config: Dict = None) -> BasePoseModel:
        """
        Create a pose estimation model
        
        Args:
            model_name: Name of the model ('mediapipe', etc.)
            config: Configuration dictionary for the model
            
        Returns:
            Instance of the requested model
            
        Raises:
            ValueError: If model_name is not supported
        """
        if model_name not in cls._models:
            raise ValueError(f"Model '{model_name}' not supported. Available models: {list(cls._models.keys())}")
        
        model_class = cls._models[model_name]
        return model_class(config)
    
    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available model names"""
        return list(cls._models.keys())