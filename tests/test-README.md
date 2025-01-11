Here’s the text converted into Markdown format for your README file:

````markdown
# Testing the Endpoints

## Start the FastAPI Server

```bash
python main.py
```
````

## Run the Client Demo (Using Webcam)

```bash
python client_demo.py
```

## Test with a Single Image

```bash
python test_image_demo.py path/to/test/image.jpg
```

## Run API Tests

```bash
pytest api_test.py
```

## Use Curl Commands from `curl_examples.sh`

### Get Available Tests

```bash
curl -X GET "http://localhost:8000/api/v1/available-tests/"
```

### Configure Test

```bash
curl -X POST "http://localhost:8000/api/v1/configure-test/" \
 -H "Content-Type: application/json" \
 -d '{"test_type": "hawkins", "include_visualization": true}'
```

# Using the Python Client in Your Code

```python
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
```

# Key Features of the Testing Setup

- Complete Python client implementation
- Webcam-based demo
- Single image testing
- API endpoint tests
- Curl examples for manual testing
- Error handling and result visualization
