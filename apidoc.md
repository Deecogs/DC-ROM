# ROM Analysis API Documentation

## Overview

The ROM (Range of Motion) Analysis API provides endpoints for analyzing body movement and measuring ranges of motion using computer vision and pose estimation technology. The primary focus is on lower back flexion analysis.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, this API does not require authentication. When deploying to production, consider adding an API key system.

## API Endpoints

### Health Check

```
GET /health
```

Checks if the API service is running properly.

**Response**:

```json
{
  "status": "healthy",
  "timestamp": 1616876420,
  "service": "ROM Analysis API",
  "version": "1.0.0"
}
```

### Get Available Tests

```
GET /api/available-tests
```

Returns a list of available ROM test types.

**Response**:

```json
{
  "available_tests": ["lowerback", "lowerback_flexion"]
}
```

### Process Frame

```
POST /api/process-frame
```

Processes a single image frame for ROM analysis.

**Request Body**:

```json
{
  "image_data": "base64_encoded_image",
  "test_type": "lowerback"
}
```

**Parameters**:

- `image_data` (string, required): Base64-encoded image data
- `test_type` (string, required): Type of ROM test to perform (e.g., "lowerback")

**Response**:

```json
{
  "test_type": "lowerback",
  "angles": [45.2, 110.7],
  "joint_positions": {
    "shoulder": { "x": 100, "y": 150 },
    "hip": { "x": 120, "y": 250 },
    "knee": { "x": 130, "y": 350 }
  },
  "processed_image": "base64_encoded_processed_image",
  "rom_data": {
    "test": "lower_back_flexion",
    "is_ready": true,
    "trunk_angle": 85.4,
    "ROM": [45.2, 110.7],
    "rom_range": 65.5,
    "position_valid": true,
    "guidance": "Good position",
    "posture_message": "Good posture",
    "ready_progress": 100.0,
    "status": "success"
  }
}
```

**Error Responses**:

- 400 Bad Request: Invalid input parameters
- 500 Internal Server Error: Processing error

### Configure Test

```
POST /api/configure-test
```

Configures parameters for a specific ROM test.

**Request Body**:

```json
{
  "test_type": "lowerback",
  "window_size": 10,
  "include_visualization": true,
  "save_results": false
}
```

**Parameters**:

- `test_type` (string, required): Type of ROM test to configure
- `window_size` (integer, optional): Size of the angle measurement window (default: 10)
- `include_visualization` (boolean, optional): Include visualization in results (default: true)
- `save_results` (boolean, optional): Save results to file (default: false)

**Response**:

```json
{
  "status": "success",
  "message": "Test configured successfully"
}
```

**Error Responses**:

- 400 Bad Request: Invalid test type or configuration parameters

## WebSocket API

### Process Frames Stream

```
WebSocket: /ws/process-frames/{client_id}?test_type=lowerback
```

Establishes a WebSocket connection for real-time processing of video frames.

**URL Parameters**:

- `client_id` (string, required): Unique identifier for the client
- `test_type` (string, optional): Type of ROM test to perform (default: "lowerback")

**Expected Input**:
The client should send base64-encoded image frames over the WebSocket connection.

**Response Format**:

```json
{
  "image": "data:image/jpeg;base64,processed_image_data",
  "rom_data": {
    "test": "lower_back_flexion",
    "is_ready": true,
    "trunk_angle": 85.4,
    "ROM": [45.2, 110.7],
    "rom_range": 65.5,
    "position_valid": true,
    "guidance": "Good position",
    "posture_message": "Good posture",
    "ready_progress": 100.0,
    "status": "success"
  },
  "timestamp": 1616876420
}
```

## ROM Data Structure

The standard ROM data structure includes:

| Field             | Type    | Description                                           |
| ----------------- | ------- | ----------------------------------------------------- |
| `test`            | string  | Type of test performed                                |
| `is_ready`        | boolean | Whether the subject is in the correct position        |
| `trunk_angle`     | float   | Current trunk angle measurement in degrees            |
| `ROM`             | array   | Min and max angles [min_angle, max_angle]             |
| `rom_range`       | float   | Total range of motion (max - min)                     |
| `position_valid`  | boolean | Whether the current position is valid for measurement |
| `guidance`        | string  | Position guidance message                             |
| `posture_message` | string  | Feedback on current posture                           |
| `ready_progress`  | float   | Percentage of readiness (0-100)                       |
| `status`          | string  | Processing status (success, error, partial)           |

## Usage Examples

### Processing a Single Frame

**Python Example**:

```python
import requests
import base64
import cv2

# Load an image
image = cv2.imread('pose.jpg')
_, buffer = cv2.imencode('.jpg', image)
image_base64 = base64.b64encode(buffer).decode('utf-8')

# Send request
response = requests.post(
    'http://localhost:8000/api/process-frame',
    json={
        'image_data': image_base64,
        'test_type': 'lowerback'
    }
)

# Parse response
result = response.json()
print(f"ROM Range: {result['rom_data']['rom_range']}°")
```

### WebSocket Connection

**JavaScript Example**:

```javascript
// Generate a client ID
const clientId = "client_" + Math.random().toString(36).substring(2, 15);

// Connect to WebSocket
const ws = new WebSocket(
  `ws://localhost:8000/ws/process-frames/${clientId}?test_type=lowerback`
);

ws.onopen = () => {
  console.log("Connected to ROM Analysis API");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Current trunk angle: ${data.rom_data.trunk_angle}°`);
  console.log(`ROM range: ${data.rom_data.rom_range}°`);

  // Display the processed image
  document.getElementById("output").src = data.image;
};

// Function to send a frame
function sendFrame(base64Image) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(base64Image);
  }
}
```

## Error Handling

The API returns standard HTTP status codes and error messages:

- 200: Successful operation
- 400: Bad request (invalid parameters)
- 404: Endpoint not found
- 500: Internal server error

Error responses include a `detail` field with a description of the error.

## Rate Limits

Currently, there are no rate limits implemented. When deploying to production, consider adding rate limiting for protection.

## Notes on ROM Analysis

- For accurate results, the subject should be visible from the side, with the body in profile view.
- The system works best with good lighting and a clear view of the subject without occlusions.
- ROM measurements stabilize over time as the system collects more data points.
- For lower back flexion, the subject should start in an upright position and bend forward slowly.
