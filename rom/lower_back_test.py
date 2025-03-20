import math
import cv2
import numpy as np
import logging
from collections import deque
from typing import Dict, Tuple, List, Optional, Any, Union

# Configure logging
logger = logging.getLogger("lower_back_test")

class LowerBackFlexionTest:
    """Class for analyzing lower back flexion range of motion."""
    
    def __init__(self, pose_detector, visualizer, window_size=10):
        """
        Initialize the LowerBackFlexionTest
        
        Args:
            pose_detector: PoseDetector instance
            visualizer: PoseVisualizer instance
            window_size: Size of the sliding window for angle calculations
        """
        self.pose_detector = pose_detector
        self.visualizer = visualizer
        self.ready_time = 0
        self.required_ready_time = 15  # Reduced from 20 for less strict check
        self.is_ready = False
        self.angle_buffer = deque(maxlen=window_size)
        self.min_angle = 180  # Start with maximum possible angle
        self.max_angle = 0    # Start with minimum possible angle
        self.current_angle = 0  # Current trunk angle
        self.last_valid_rom_data = None  # Store last valid ROM data
        
        # Define key points for lower back flexion test
        self.key_points = [
            11,  # Left shoulder
            12,  # Right shoulder
            23,  # Left hip
            24,  # Right hip
            25,  # Left knee
            26   # Right knee
        ]
        
        logger.info("LowerBackFlexionTest initialized")

    def get_default_rom_data(self) -> Dict[str, Any]:
        """
        Create a default ROM data structure. This ensures we always 
        return a consistent data structure, even in error cases.
        
        Returns:
            Dictionary with default ROM values
        """
        rom_range = max(0, self.max_angle - self.min_angle)
        
        return {
            "test": "lower_back_flexion",
            "is_ready": self.is_ready,
            "trunk_angle": round(self.current_angle, 1),
            "ROM": [round(self.min_angle, 1), round(self.max_angle, 1)],
            "rom_range": round(rom_range, 1),
            "position_valid": False,
            "guidance": "Position not detected. Please stand with full body visible.",
            "posture_message": "",
            "ready_progress": round((self.ready_time / self.required_ready_time) * 100, 0),
            "status": "partial"
        }

    @staticmethod
    def calculate_angle(p1: Union[List, Tuple], p2: Union[List, Tuple], p3: Union[List, Tuple]) -> float:
        """
        Calculate angle between three points using the dot product method.
        p2 is the vertex point.
        
        Args:
            p1, p2, p3: Points as tuples or lists (x, y, [z])
            
        Returns:
            Angle in degrees
        """
        try:
            # Extract x, y coordinates
            p1 = np.array(p1[:2])
            p2 = np.array(p2[:2])
            p3 = np.array(p3[:2])

            # Vectors from the vertex
            vector1 = p1 - p2
            vector2 = p3 - p2
            
            # Handle zero vectors
            if np.all(vector1 == 0) or np.all(vector2 == 0):
                return 0.0

            # Compute the cosine of the angle
            dot_product = np.dot(vector1, vector2)
            norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
            
            # Avoid division by zero
            if norm_product == 0:
                return 0.0
                
            cosine_angle = dot_product / norm_product
            
            # Handle numerical errors that could put cosine outside [-1, 1]
            cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

            # Compute the angle in degrees
            angle = np.degrees(np.arccos(cosine_angle))
            return angle
        except Exception as e:
            logger.error(f"Error calculating angle: {str(e)}")
            return 0.0

    def check_initial_position(self, frame, coords) -> Tuple[bool, str]:
        """
        Check if the person is in the correct starting position.
        Less strict version with fewer checks.
        
        Args:
            frame: Video frame
            coords: Dictionary of landmark coordinates
            
        Returns:
            Tuple of (is_position_valid, guidance_message)
        """
        try:
            h, w, _ = frame.shape
            messages = []
            is_valid = True

            # Check if required key points are detected
            required_points = [11, 12, 23, 24]  # Shoulders and hips
            for point in required_points:
                if point not in coords:
                    return False, "Cannot detect upper body. Please face the camera."

            # Check if person is facing the camera (using shoulder width)
            left_shoulder = coords[11]
            right_shoulder = coords[12]
            shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
            if shoulder_width < w * 0.10:  # Reduced from 0.15
                messages.append("Turn to face the camera")
                is_valid = False

            # Check if person is centered (simplified check)
            center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            if center_x < w * 0.2:
                messages.append("Move right")
                is_valid = False
            elif center_x > w * 0.8:
                messages.append("Move left")
                is_valid = False

            message = " | ".join(messages) if messages else "Good position"
            return is_valid, message
            
        except Exception as e:
            logger.error(f"Error checking initial position: {str(e)}")
            return False, "Position check error"

    def draw_pose_guidance(self, frame, message: str):
        """
        Draw guidance overlay on frame.
        
        Args:
            frame: Video frame
            message: Guidance message to display
            
        Returns:
            Frame with guidance overlay
        """
        try:
            h, w, _ = frame.shape

            # Draw semi-transparent overlay at bottom
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            # Draw guidance text
            self.visualizer.put_text(
                frame,
                f"Position Guide: {message}",
                (20, h - 50),
                color='white',
                scale=0.7
            )

            # Draw progress bar if in correct position
            if self.ready_time > 0:
                progress = (self.ready_time / self.required_ready_time) * (w - 40)
                cv2.rectangle(frame, (20, h - 30), (w - 20, h - 20), (255, 255, 255), 1)
                cv2.rectangle(frame, (20, h - 30), (int(20 + progress), h - 20), (0, 255, 0), -1)

            return frame
            
        except Exception as e:
            logger.error(f"Error drawing pose guidance: {str(e)}")
            return frame

    def update_rom(self, angle: float) -> None:
        """
        Update ROM based on current angle measurement.
        
        Args:
            angle: Current angle measurement
        """
        try:
            if not math.isnan(angle) and angle > 0:
                # Store current angle
                self.current_angle = angle
                
                # Add the new angle to the buffer
                self.angle_buffer.append(angle)
                
                # Only update if we have enough data
                if len(self.angle_buffer) > 3:
                    # Use the middle 80% of values to avoid outliers
                    sorted_angles = sorted(self.angle_buffer)
                    filtered_angles = sorted_angles[1:-1] if len(sorted_angles) > 4 else sorted_angles
                    
                    # Update min and max
                    current_min = min(filtered_angles)
                    current_max = max(filtered_angles)
                    
                    # Only update if the new values are within reasonable bounds
                    if current_min < self.min_angle and current_min > 10:  # Avoid extreme values
                        self.min_angle = current_min
                        
                    if current_max > self.max_angle and current_max < 170:  # Avoid extreme values
                        self.max_angle = current_max
        except Exception as e:
            logger.error(f"Error updating ROM: {str(e)}")

    def process_frame(self, frame):
        """
        Process a single frame for Lower Back Flexion test.
        Always returns a valid ROM data structure.
        
        Args:
            frame: Video frame
            
        Returns:
            Tuple of (processed_frame, rom_data)
        """
        try:
            # Get default ROM data as fallback
            default_rom_data = self.get_default_rom_data()
            
            # Ensure we have a valid frame
            if frame is None or frame.size == 0:
                logger.warning("Empty or invalid frame received")
                return frame, default_rom_data
            
            # Detect pose landmarks
            landmarks = self.pose_detector.find_pose(frame)
            
            if not landmarks:
                logger.debug("No landmarks detected in frame")
                # Use last valid data if available, otherwise return default
                return frame, self.last_valid_rom_data if self.last_valid_rom_data else default_rom_data
            
            # Get landmark coordinates
            coords = self.pose_detector.get_landmark_coordinates(frame, landmarks)
            
            # Check if we have the required landmarks
            required_landmarks = [11, 23, 25]  # shoulder, hip, knee
            if not all(point in coords for point in required_landmarks):
                guidance_msg = "Cannot see full body. Please step back."
                default_rom_data["guidance"] = guidance_msg
                return frame, default_rom_data
            
            # First check initial position
            is_valid_position, guidance_message = self.check_initial_position(frame, coords)

            # Update ready state
            if is_valid_position:
                self.ready_time = min(self.ready_time + 1, self.required_ready_time)
                if self.ready_time >= self.required_ready_time:
                    self.is_ready = True
            else:
                self.ready_time = max(self.ready_time - 1, 0)
                if self.ready_time == 0:
                    self.is_ready = False

            # Draw position guidance
            frame = self.draw_pose_guidance(frame, guidance_message)

            # Get relevant landmarks for Lower Back Flexion
            shoulder = coords[11]  # Left shoulder
            hip = coords[23]       # Left hip
            knee = coords[25]      # Left knee

            # Calculate trunk angle
            trunk_angle = self.calculate_angle(shoulder, hip, knee)
            self.current_angle = trunk_angle  # Store current angle

            # Update ROM if ready
            if self.is_ready:
                self.update_rom(trunk_angle)

            # Visualize landmarks and angles
            try:
                self.visualizer.draw_landmark_point(frame, shoulder[0], shoulder[1], 'white')
                self.visualizer.draw_landmark_point(frame, hip[0], hip[1], 'white')
                self.visualizer.draw_landmark_point(frame, knee[0], knee[1], 'white')
                self.visualizer.draw_angle(frame, shoulder, hip, knee, trunk_angle)
            except Exception as vis_error:
                logger.warning(f"Visualization error: {str(vis_error)}")

            # Add feedback based on trunk angle
            posture_message = ""
            if self.is_ready:
                if 70 <= trunk_angle <= 110:  # Wider acceptance range
                    posture_message = "Good posture"
                    self.visualizer.put_text(frame, posture_message, (10, 60), color='green')
                else:
                    posture_message = "Adjust posture"
                    self.visualizer.put_text(frame, posture_message, (10, 60), color='red')

            # Calculate ROM range
            rom_range = self.max_angle - self.min_angle
            
            # Create ROM data with guaranteed structure
            rom_data = {
                "test": "lower_back_flexion",
                "is_ready": self.is_ready,
                "trunk_angle": round(trunk_angle, 1),
                "ROM": [round(self.min_angle, 1), round(self.max_angle, 1)],
                "rom_range": round(rom_range, 1),
                "position_valid": is_valid_position,
                "guidance": guidance_message,
                "posture_message": posture_message,
                "ready_progress": round((self.ready_time / self.required_ready_time) * 100, 0),
                "status": "success"
            }
            
            # Store this as the last valid data
            self.last_valid_rom_data = rom_data
            
            return frame, rom_data
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            
            # Return default ROM data structure to ensure consistent output
            default_rom_data = self.get_default_rom_data()
            default_rom_data["status"] = "error"
            default_rom_data["error_message"] = str(e)
            
            return frame, default_rom_data
# import math
# import cv2
# import numpy as np
# import logging
# from collections import deque
# from typing import Dict, Tuple, List, Optional, Any, Union

# # Configure logging
# logger = logging.getLogger("lower_back_test")

# class LowerBackFlexionTest:
#     """Class for analyzing lower back flexion range of motion."""
    
#     def __init__(self, pose_detector, visualizer, window_size=10):
#         """
#         Initialize the LowerBackFlexionTest
        
#         Args:
#             pose_detector: PoseDetector instance
#             visualizer: PoseVisualizer instance
#             window_size: Size of the sliding window for angle calculations
#         """
#         self.pose_detector = pose_detector
#         self.visualizer = visualizer
#         self.ready_time = 0
#         self.required_ready_time = 15  # Reduced from 20 for less strict check
#         self.is_ready = False
#         self.angle_buffer = deque(maxlen=window_size)
#         self.min_angle = 180  # Start with maximum possible angle
#         self.max_angle = 0    # Start with minimum possible angle
#         self.last_valid_rom_data = None  # Store last valid ROM data
        
#         # Define key points for lower back flexion test
#         self.key_points = [
#             11,  # Left shoulder
#             12,  # Right shoulder
#             23,  # Left hip
#             24,  # Right hip
#             25,  # Left knee
#             26   # Right knee
#         ]
        
#         logger.info("LowerBackFlexionTest initialized")

#     @staticmethod
#     def calculate_angle(p1: Union[List, Tuple], p2: Union[List, Tuple], p3: Union[List, Tuple]) -> float:
#         """
#         Calculate angle between three points using the dot product method.
#         p2 is the vertex point.
        
#         Args:
#             p1, p2, p3: Points as tuples or lists (x, y, [z])
            
#         Returns:
#             Angle in degrees
#         """
#         try:
#             # Extract x, y coordinates
#             p1 = np.array(p1[:2])
#             p2 = np.array(p2[:2])
#             p3 = np.array(p3[:2])

#             # Vectors from the vertex
#             vector1 = p1 - p2
#             vector2 = p3 - p2
            
#             # Handle zero vectors
#             if np.all(vector1 == 0) or np.all(vector2 == 0):
#                 return 0.0

#             # Compute the cosine of the angle
#             dot_product = np.dot(vector1, vector2)
#             norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
            
#             # Avoid division by zero
#             if norm_product == 0:
#                 return 0.0
                
#             cosine_angle = dot_product / norm_product
            
#             # Handle numerical errors that could put cosine outside [-1, 1]
#             cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

#             # Compute the angle in degrees
#             angle = np.degrees(np.arccos(cosine_angle))
#             return angle
#         except Exception as e:
#             logger.error(f"Error calculating angle: {str(e)}")
#             return 0.0

#     def check_initial_position(self, frame, coords) -> Tuple[bool, str]:
#         """
#         Check if the person is in the correct starting position.
#         Less strict version with fewer checks.
        
#         Args:
#             frame: Video frame
#             coords: Dictionary of landmark coordinates
            
#         Returns:
#             Tuple of (is_position_valid, guidance_message)
#         """
#         try:
#             h, w, _ = frame.shape
#             messages = []
#             is_valid = True

#             # Check if required key points are detected
#             required_points = [11, 12, 23, 24]  # Shoulders and hips
#             for point in required_points:
#                 if point not in coords:
#                     return False, "Cannot detect upper body. Please face the camera."

#             # Check if person is facing the camera (using shoulder width)
#             left_shoulder = coords[11]
#             right_shoulder = coords[12]
#             shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
#             if shoulder_width < w * 0.10:  # Reduced from 0.15
#                 messages.append("Turn to face the camera")
#                 is_valid = False

#             # Check if person is centered (simplified check)
#             center_x = (left_shoulder[0] + right_shoulder[0]) / 2
#             if center_x < w * 0.2:
#                 messages.append("Move right")
#                 is_valid = False
#             elif center_x > w * 0.8:
#                 messages.append("Move left")
#                 is_valid = False

#             message = " | ".join(messages) if messages else "Good position"
#             return is_valid, message
            
#         except Exception as e:
#             logger.error(f"Error checking initial position: {str(e)}")
#             return False, "Position check error"

#     def draw_pose_guidance(self, frame, message: str):
#         """
#         Draw guidance overlay on frame.
        
#         Args:
#             frame: Video frame
#             message: Guidance message to display
            
#         Returns:
#             Frame with guidance overlay
#         """
#         try:
#             h, w, _ = frame.shape

#             # Draw semi-transparent overlay at bottom
#             overlay = frame.copy()
#             cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 0), -1)
#             cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

#             # Draw guidance text
#             self.visualizer.put_text(
#                 frame,
#                 f"Position Guide: {message}",
#                 (20, h - 50),
#                 color='white',
#                 scale=0.7
#             )

#             # Draw progress bar if in correct position
#             if self.ready_time > 0:
#                 progress = (self.ready_time / self.required_ready_time) * (w - 40)
#                 cv2.rectangle(frame, (20, h - 30), (w - 20, h - 20), (255, 255, 255), 1)
#                 cv2.rectangle(frame, (20, h - 30), (int(20 + progress), h - 20), (0, 255, 0), -1)

#             return frame
            
#         except Exception as e:
#             logger.error(f"Error drawing pose guidance: {str(e)}")
#             return frame

#     def update_rom(self, angle: float) -> None:
#         """
#         Update ROM based on current angle measurement.
        
#         Args:
#             angle: Current angle measurement
#         """
#         try:
#             if not math.isnan(angle) and angle > 0:
#                 # Add the new angle to the buffer
#                 self.angle_buffer.append(angle)
                
#                 # Only update if we have enough data
#                 if len(self.angle_buffer) > 3:
#                     # Use the middle 80% of values to avoid outliers
#                     sorted_angles = sorted(self.angle_buffer)
#                     filtered_angles = sorted_angles[1:-1] if len(sorted_angles) > 4 else sorted_angles
                    
#                     # Update min and max
#                     current_min = min(filtered_angles)
#                     current_max = max(filtered_angles)
                    
#                     # Only update if the new values are within reasonable bounds
#                     if current_min < self.min_angle and current_min > 10:  # Avoid extreme values
#                         self.min_angle = current_min
                        
#                     if current_max > self.max_angle and current_max < 170:  # Avoid extreme values
#                         self.max_angle = current_max
#         except Exception as e:
#             logger.error(f"Error updating ROM: {str(e)}")

#     def process_frame(self, frame):
#         """
#         Process a single frame for Lower Back Flexion test.
        
#         Args:
#             frame: Video frame
            
#         Returns:
#             Tuple of (processed_frame, rom_data)
#         """
#         try:
#             # Create default ROM data structure
#             default_rom_data = {
#                 "test": "lower_back_flexion",
#                 "is_ready": False,
#                 "trunk_angle": 0,
#                 "ROM": [self.min_angle, self.max_angle],
#                 "position_valid": False,
#                 "guidance": "Processing...",
#                 "posture_message": "",
#                 "ready_progress": 0,
#                 "status": "processing"
#             }
            
#             # Detect pose landmarks
#             landmarks = self.pose_detector.find_pose(frame)
            
#             if not landmarks:
#                 # Use last valid data if available, otherwise return default
#                 return frame, self.last_valid_rom_data if self.last_valid_rom_data else default_rom_data
            
#             # Get landmark coordinates
#             coords = self.pose_detector.get_landmark_coordinates(frame, landmarks)
            
#             # Check if we have the required landmarks
#             required_landmarks = [11, 23, 25]  # shoulder, hip, knee
#             if not all(point in coords for point in required_landmarks):
#                 default_rom_data["guidance"] = "Cannot see full body. Please step back."
#                 return frame, default_rom_data
            
#             # First check initial position
#             is_valid_position, guidance_message = self.check_initial_position(frame, coords)

#             # Update ready state
#             if is_valid_position:
#                 self.ready_time = min(self.ready_time + 1, self.required_ready_time)
#                 if self.ready_time >= self.required_ready_time:
#                     self.is_ready = True
#             else:
#                 self.ready_time = max(self.ready_time - 1, 0)
#                 if self.ready_time == 0:
#                     self.is_ready = False

#             # Draw position guidance
#             frame = self.draw_pose_guidance(frame, guidance_message)

#             # Get relevant landmarks for Lower Back Flexion
#             shoulder = coords[11]  # Left shoulder
#             hip = coords[23]       # Left hip
#             knee = coords[25]      # Left knee

#             # Calculate trunk angle
#             trunk_angle = self.calculate_angle(shoulder, hip, knee)

#             # Update ROM if ready
#             if self.is_ready:
#                 self.update_rom(trunk_angle)

#             # Visualize landmarks and angles
#             try:
#                 self.visualizer.draw_landmark_point(frame, shoulder[0], shoulder[1], 'white')
#                 self.visualizer.draw_landmark_point(frame, hip[0], hip[1], 'white')
#                 self.visualizer.draw_landmark_point(frame, knee[0], knee[1], 'white')
#                 self.visualizer.draw_angle(frame, shoulder, hip, knee, trunk_angle)
#             except Exception as vis_error:
#                 logger.warning(f"Visualization error: {str(vis_error)}")

#             # Add feedback based on trunk angle
#             posture_message = ""
#             if self.is_ready:
#                 if 70 <= trunk_angle <= 110:  # Wider acceptance range
#                     posture_message = "Good posture"
#                     self.visualizer.put_text(frame, posture_message, (10, 60), color='green')
#                 else:
#                     posture_message = "Adjust posture"
#                     self.visualizer.put_text(frame, posture_message, (10, 60), color='red')

#             # Calculate ROM range
#             rom_range = self.max_angle - self.min_angle
            
#             # Create ROM data
#             rom_data = {
#                 "test": "lower_back_flexion",
#                 "is_ready": self.is_ready,
#                 "trunk_angle": round(trunk_angle, 1),
#                 "ROM": [round(self.min_angle, 1), round(self.max_angle, 1)],
#                 "rom_range": round(rom_range, 1),
#                 "position_valid": is_valid_position,
#                 "guidance": guidance_message,
#                 "posture_message": posture_message,
#                 "ready_progress": round((self.ready_time / self.required_ready_time) * 100, 0),
#                 "status": "success"
#             }
            
#             # Store this as the last valid data
#             self.last_valid_rom_data = rom_data
            
#             return frame, rom_data
            
#         except Exception as e:
#             logger.error(f"Error processing frame: {str(e)}")
#             error_message = f"Processing error: {str(e)}"
            
#             # Return basic error data and original frame
#             return frame, {
#                 "test": "lower_back_flexion",
#                 "error": error_message,
#                 "status": "error"
#             }