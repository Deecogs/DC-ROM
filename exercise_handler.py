import cv2
from utils.pose_detector import PoseDetector
from utils.visualization import PoseVisualizer
from rom.hawkins_test import HawkinsTest
from rom.lower_back_test import LowerBackFlexionTest  # Assuming this is your lower back test class


class ExerciseHandler:
    def __init__(self, exercise_name):
        """
        Initialize the appropriate exercise handler based on the requested exercise.
        :param exercise_name: Name of the exercise (e.g., "hawkins", "lowerback").
        """
        self.exercise_name = exercise_name.lower()
        self.pose_detector = PoseDetector()
        self.visualizer = PoseVisualizer()

        # Dynamically load the appropriate test class
        if self.exercise_name == "hawkins":
            self.exercise_test = HawkinsTest(self.pose_detector, self.visualizer)
        elif self.exercise_name == "lowerback":
            self.exercise_test = LowerBackFlexionTest(self.pose_detector, self.visualizer)
        else:
            raise ValueError(f"Unsupported exercise: {exercise_name}")

    def process_frame(self, frame):
        """
        Process a single frame through the selected exercise test.
        :param frame: Input video frame.
        :return: Processed frame with visualization and ROM data.
        """
        processed_frame, rom_data = self.exercise_test.process_frame(frame)

        # Add exercise-specific instructions on the frame
        if self.exercise_name == "hawkins":
            instructions = "Stand in the center and raise your left arm."
        elif self.exercise_name == "lowerback":
            instructions = "Stand straight and perform the flexion movement."

        cv2.putText(
            processed_frame,
            instructions,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        return processed_frame, rom_data


if __name__ == "__main__":
    print("This file is meant to provide methods for exercise handling.")
    print("Use app.py to run the WebSocket service.")
