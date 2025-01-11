from test_client import ROMCalculatorClient

# Initialize client
client = ROMCalculatorClient()

# Get available tests
tests = client.get_available_tests()
print(f"Available tests: {tests}")

# Configure test
config_result = client.configure_test("hawkins", include_visualization=True)
print(f"Configuration result: {config_result}")

# Process a frame
import cv2
image = cv2.imread("test_image.jpg")
result = client.process_frame(image, test_type="hawkins")
print(f"ROM Results: {result['angles']}")