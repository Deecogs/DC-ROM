import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.processing.frame_processor import FrameProcessor
from src.processing.interpolation import interpolate_missing_keypoints
from src.processing.filters import FilterFactory

class VideoProcessor:
    """Process entire videos with optimization"""
    
    def __init__(self):
        self.frame_processor = FrameProcessor()
        self.filter_factory = FilterFactory()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_video_async(
        self,
        video_path: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        skip_frames: int = 1,
        apply_filter: bool = True,
        filter_type: str = "butterworth"
    ) -> Dict:
        """
        Process video asynchronously
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            skip_frames: Process every Nth frame
            apply_filter: Whether to apply filtering
            filter_type: Type of filter to apply
            
        Returns:
            Dictionary with processed results
        """
        # Run processing in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor,
            self._process_video_sync,
            video_path,
            start_time,
            end_time,
            skip_frames,
            apply_filter,
            filter_type
        )
        
        return results
    
    def _process_video_sync(
        self,
        video_path: str,
        start_time: Optional[float],
        end_time: Optional[float],
        skip_frames: int,
        apply_filter: bool,
        filter_type: str
    ) -> Dict:
        """Synchronous video processing"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.frame_processor.set_fps(fps)
        
        # Calculate frame range
        start_frame = int(start_time * fps) if start_time else 0
        end_frame = int(end_time * fps) if end_time else total_frames
        
        # Process frames
        raw_results = []
        frame_count = 0
        
        if start_frame > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        while cap.isOpened() and frame_count < (end_frame - start_frame):
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % skip_frames == 0:
                timestamp = (start_frame + frame_count) / fps
                result = self.frame_processor.process_frame(frame, timestamp)
                raw_results.append(result)
            
            frame_count += 1
        
        cap.release()
        
        # Post-process results
        if apply_filter and len(raw_results) > 10:
            filtered_results = self._apply_filtering(raw_results, filter_type, fps)
        else:
            filtered_results = raw_results
        
        return {
            'video_info': {
                'fps': fps,
                'total_frames': total_frames,
                'width': width,
                'height': height,
                'duration': total_frames / fps if fps > 0 else 0
            },
            'processed_frames': len(filtered_results),
            'results': filtered_results
        }
    
    def _apply_filtering(
        self,
        results: List[Dict],
        filter_type: str,
        fps: float
    ) -> List[Dict]:
        """Apply filtering to smooth results"""
        # Extract time series data for filtering
        persons_data = self._extract_persons_timeseries(results)
        
        # Apply filters to each person's data
        filter_func = self.filter_factory.get_filter(filter_type, fps)
        
        for person_id, person_data in persons_data.items():
            # Filter keypoints
            for keypoint_name in person_data['keypoints']:
                for coord in ['x', 'y']:
                    values = person_data['keypoints'][keypoint_name][coord]
                    if values:
                        filtered_values = filter_func(np.array(values))
                        person_data['keypoints'][keypoint_name][coord] = filtered_values.tolist()
            
            # Filter angles
            for angle_type in ['joint_angles', 'segment_angles']:
                for angle_name in person_data['angles'][angle_type]:
                    values = person_data['angles'][angle_type][angle_name]
                    if values and not all(v is None for v in values):
                        # Handle None values
                        valid_indices = [i for i, v in enumerate(values) if v is not None]
                        if valid_indices:
                            valid_values = [values[i] for i in valid_indices]
                            filtered_values = filter_func(np.array(valid_values))
                            
                            # Put filtered values back
                            for idx, filtered_val in zip(valid_indices, filtered_values):
                                values[idx] = float(filtered_val)
        
        # Reconstruct results
        return self._reconstruct_results(results, persons_data)
    
    def _extract_persons_timeseries(self, results: List[Dict]) -> Dict:
        """Extract time series data for each person"""
        persons_data = {}
        
        for frame_result in results:
            for person in frame_result['persons']:
                person_id = person['person_id']
                
                if person_id not in persons_data:
                    persons_data[person_id] = {
                        'keypoints': {},
                        'angles': {'joint_angles': {}, 'segment_angles': {}}
                    }
                
                # Extract keypoints
                for kp_name, kp_data in person['keypoints'].items():
                    if kp_name not in persons_data[person_id]['keypoints']:
                        persons_data[person_id]['keypoints'][kp_name] = {
                            'x': [], 'y': [], 'confidence': []
                        }
                    
                    persons_data[person_id]['keypoints'][kp_name]['x'].append(kp_data['x'])
                    persons_data[person_id]['keypoints'][kp_name]['y'].append(kp_data['y'])
                    persons_data[person_id]['keypoints'][kp_name]['confidence'].append(
                        kp_data['confidence']
                    )
                
                # Extract angles
                for angle_type in ['joint_angles', 'segment_angles']:
                    for angle_name, angle_value in person['angles'][angle_type].items():
                        if angle_name not in persons_data[person_id]['angles'][angle_type]:
                            persons_data[person_id]['angles'][angle_type][angle_name] = []
                        
                        persons_data[person_id]['angles'][angle_type][angle_name].append(
                            angle_value
                        )
        
        return persons_data
    
    def _reconstruct_results(
        self,
        original_results: List[Dict],
        filtered_persons_data: Dict
    ) -> List[Dict]:
        """Reconstruct results with filtered data"""
        reconstructed = []
        
        for frame_idx, frame_result in enumerate(original_results):
            new_frame_result = frame_result.copy()
            new_persons = []
            
            for person in frame_result['persons']:
                person_id = person['person_id']
                
                if person_id in filtered_persons_data:
                    new_person = person.copy()
                    
                    # Update keypoints
                    for kp_name in person['keypoints']:
                        if kp_name in filtered_persons_data[person_id]['keypoints']:
                            kp_data = filtered_persons_data[person_id]['keypoints'][kp_name]
                            if frame_idx < len(kp_data['x']):
                                new_person['keypoints'][kp_name] = {
                                    'x': kp_data['x'][frame_idx],
                                    'y': kp_data['y'][frame_idx],
                                    'confidence': kp_data['confidence'][frame_idx]
                                }
                    
                    # Update angles
                    for angle_type in ['joint_angles', 'segment_angles']:
                        for angle_name in person['angles'][angle_type]:
                            angle_data = filtered_persons_data[person_id]['angles'][angle_type]
                            if angle_name in angle_data and frame_idx < len(angle_data[angle_name]):
                                new_person['angles'][angle_type][angle_name] = \
                                    angle_data[angle_name][frame_idx]
                    
                    new_persons.append(new_person)
            
            new_frame_result['persons'] = new_persons
            reconstructed.append(new_frame_result)
        
        return reconstructed