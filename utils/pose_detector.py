# utils/pose_detector.py
import mediapipe as mp
import cv2
import numpy as np
import logging

logger = logging.getLogger("pose_detector")

class PoseDetector:
    def __init__(self, 
                 model_complexity=1, 
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5,
                 enable_segmentation=False):
        """
        Initialize the MediaPipe Holistic model for comprehensive pose detection.
        
        Args:
            model_complexity: Model complexity (0, 1, or 2)
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
            enable_segmentation: Whether to enable segmentation
        """
        logger.info("Initializing Holistic Pose Detector")
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=model_complexity,
            smooth_landmarks=True,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Create a mapping from Holistic pose landmarks to indices (similar to what we had with Pose)
        self.pose_landmark_to_index = {
            # We'll map the landmark enum values to the same index values
            # they would have in the pose_landmarks
            getattr(self.mp_holistic.PoseLandmark, name): getattr(self.mp_holistic.PoseLandmark, name).value
            for name in dir(self.mp_holistic.PoseLandmark)
            if not name.startswith('__') and not callable(getattr(self.mp_holistic.PoseLandmark, name))
        }
        
        logger.info("Holistic Pose Detector initialized successfully")
        
    def find_pose(self, frame):
        """
        Process frame and return pose landmarks.
        
        Args:
            frame: Input image frame
            
        Returns:
            Pose landmarks if detected, else None
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.holistic.process(rgb_frame)
            
            # Return pose landmarks
            return results.pose_landmarks
        
        except Exception as e:
            logger.error(f"Error finding pose: {str(e)}")
            return None
    
    def get_landmark_coordinates(self, frame, landmarks):
        """
        Convert normalized landmarks to pixel coordinates.
        
        Args:
            frame: Input image frame
            landmarks: Detected pose landmarks
            
        Returns:
            Dictionary of landmark coordinates indexed by landmark index
        """
        try:
            if not landmarks:
                return {}
                
            h, w, _ = frame.shape
            coordinates = {}
            
            for idx, landmark in enumerate(landmarks.landmark):
                # Convert normalized coordinates to pixel values
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                z = landmark.z  # Depth (relative to hip center)
                visibility = landmark.visibility if hasattr(landmark, 'visibility') else 1.0
                
                # Only include landmarks with reasonable visibility
                if visibility > 0.5:
                    coordinates[idx] = (x, y, z, visibility)
                else:
                    coordinates[idx] = (x, y, z, visibility)  # Still include but with low visibility marker
            
            return coordinates
            
        except Exception as e:
            logger.error(f"Error getting landmark coordinates: {str(e)}")
            return {}
    
    def draw_landmarks(self, frame, landmarks):
        """
        Draw pose landmarks on the frame.
        
        Args:
            frame: Input image frame
            landmarks: Detected pose landmarks
            
        Returns:
            Frame with landmarks drawn
        """
        try:
            if landmarks:
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    landmarks,
                    self.mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
            return frame
            
        except Exception as e:
            logger.error(f"Error drawing landmarks: {str(e)}")
            return frame
    
    def get_full_body_results(self, frame):
        """
        Get comprehensive holistic results including face, pose, hands.
        
        Args:
            frame: Input image frame
            
        Returns:
            Dictionary with all detected landmarks and processed frame
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame with holistic model
            results = self.holistic.process(rgb_frame)
            
            # Create visualization image
            annotated_frame = frame.copy()
            
            # Draw face landmarks
            if results.face_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.face_landmarks,
                    self.mp_holistic.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
            
            # Draw pose landmarks
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.pose_landmarks,
                    self.mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
            
            # Draw left hand landmarks
            if results.left_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.left_hand_landmarks,
                    self.mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    connection_drawing_spec=self.mp_drawing_styles.get_default_hand_connections_style()
                )
            
            # Draw right hand landmarks
            if results.right_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.right_hand_landmarks,
                    self.mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    connection_drawing_spec=self.mp_drawing_styles.get_default_hand_connections_style()
                )
            
            # Extract coordinates for all detected landmarks
            h, w, _ = frame.shape
            
            # Process pose landmarks
            pose_coords = {}
            if results.pose_landmarks:
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    visibility = landmark.visibility
                    pose_coords[idx] = (x, y, z, visibility)
            
            return {
                'pose_landmarks': results.pose_landmarks,
                'face_landmarks': results.face_landmarks,
                'left_hand_landmarks': results.left_hand_landmarks,
                'right_hand_landmarks': results.right_hand_landmarks,
                'pose_coordinates': pose_coords,
                'annotated_frame': annotated_frame
            }
            
        except Exception as e:
            logger.error(f"Error getting full body results: {str(e)}")
            return {
                'annotated_frame': frame
            }