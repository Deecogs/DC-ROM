# rom/base_test.py
from abc import ABC, abstractmethod

class ROMTest(ABC):
    def __init__(self, pose_detector, visualizer):
        self.pose_detector = pose_detector
        self.visualizer = visualizer
    
    @abstractmethod
    def process_frame(self, frame):
        """Process a single frame and return processed frame and ROM data."""
        pass
    
    @abstractmethod
    def calculate_rom(self, landmarks):
        """Calculate range of motion from landmarks."""
        pass
    
    @abstractmethod
    def visualize_results(self, frame, rom_data):
        """Visualize ROM results on frame."""
        pass