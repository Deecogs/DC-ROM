import cv2

import cv2

def draw_overlay(frame, overlay_image=None):
    """
    Draw an overlay on the frame. If no overlay_image is provided, return the frame as is.

    Args:
        frame (np.ndarray): The base image/frame.
        overlay_image (np.ndarray, optional): The overlay image to blend with the frame.

    Returns:
        np.ndarray: The frame with the overlay applied, or the original frame if no overlay is provided.
    """
    # If no overlay image is provided, return the original frame
    if overlay_image is None:
        return frame

    # Resize the overlay image to match the frame dimensions
    resized_overlay = cv2.resize(overlay_image, (frame.shape[1], frame.shape[0]))

    # Ensure both images have the same number of channels
    if len(resized_overlay.shape) != len(frame.shape):
        if len(resized_overlay.shape) == 2:  # Overlay is grayscale
            resized_overlay = cv2.cvtColor(resized_overlay, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 2:  # Frame is grayscale
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    # Apply the overlay with transparency
    blended = cv2.addWeighted(resized_overlay, 0.5, frame, 0.5, 0)
    return blended


def draw_diamond(frame, landmarks):
    # Draw a diamond for elbow flexion visualization
    pass

def annotate_elbow_angle(frame, angle):
    cv2.putText(frame, f"Elbow Angle: {angle:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
