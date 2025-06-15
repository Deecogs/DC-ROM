import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from typing import Callable

class FilterFactory:
    """Factory for creating different filter types"""
    
    def get_filter(self, filter_type: str, fps: float) -> Callable:
        """
        Get a filter function
        
        Args:
            filter_type: Type of filter ('butterworth', 'gaussian', 'median')
            fps: Frames per second for frequency-based filters
            
        Returns:
            Filter function that takes a 1D array and returns filtered array
        """
        if filter_type == 'butterworth':
            return self._create_butterworth_filter(fps)
        elif filter_type == 'gaussian':
            return self._create_gaussian_filter()
        elif filter_type == 'median':
            return self._create_median_filter()
        else:
            # Return identity function if filter type not recognized
            return lambda x: x
    
    def _create_butterworth_filter(self, fps: float) -> Callable:
        """Create Butterworth filter function"""
        def butterworth_filter(data: np.ndarray) -> np.ndarray:
            if len(data) < 10:
                return data
            
            # Filter parameters
            order = 4
            cutoff = 6.0  # Hz
            
            # Normalize cutoff frequency
            nyquist = fps / 2
            normal_cutoff = cutoff / nyquist
            
            if normal_cutoff >= 1:
                normal_cutoff = 0.99
            
            # Create filter
            b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
            
            # Apply filter (forward-backward to avoid phase shift)
            try:
                filtered = signal.filtfilt(b, a, data)
                return filtered
            except:
                # If filtering fails, return original data
                return data
        
        return butterworth_filter
    
    def _create_gaussian_filter(self) -> Callable:
        """Create Gaussian filter function"""
        def gaussian_filter(data: np.ndarray) -> np.ndarray:
            if len(data) < 3:
                return data
            
            # Apply Gaussian filter with sigma=1
            try:
                filtered = gaussian_filter1d(data, sigma=1.0)
                return filtered
            except:
                return data
        
        return gaussian_filter
    
    def _create_median_filter(self) -> Callable:
        """Create median filter function"""
        def median_filter(data: np.ndarray) -> np.ndarray:
            if len(data) < 3:
                return data
            
            # Apply median filter with kernel size 3
            try:
                filtered = signal.medfilt(data, kernel_size=3)
                return filtered
            except:
                return data
        
        return median_filter