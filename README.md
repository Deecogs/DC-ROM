{
"frame_id": 0,
"timestamp": 0.033,
"processing_time_ms": 15.2,
"persons": [
{
"person_id": 0,
"tracking_confidence": 0.95,
"keypoints": {
"nose": {"x": 320, "y": 240, "confidence": 0.98},
"left_shoulder": {"x": 300, "y": 280, "confidence": 0.95},
// ... all keypoints
},
"angles": {
"joint_angles": {
"right_knee": 145.2,
"left_knee": 142.8,
"right_hip": 178.5,
// ... all joint angles
},
"segment_angles": {
"right_thigh": 85.3,
"left_thigh": 83.7,
"trunk": 92.1,
// ... all segment angles
}
},
"metrics": {
"height_pixels": 450,
"center_of_mass": {"x": 320, "y": 350},
"velocity": {"x": 2.5, "y": 0.1},
"visible_side": "right",
"movement_direction": "left_to_right"
}
}
],
"frame_metrics": {
"detected_persons": 2,
"average_confidence": 0.89,
"processing_fps": 65
}
}

POST /api/analyze/video - Process uploaded video
POST /api/analyze/image - Process single image
WS /api/analyze/stream - WebSocket for real-time streaming
GET /api/results/{job_id} - Get processing results
GET /api/angles/definitions - Get angle calculation info
POST /api/config - Update processing configuration
GET /api/health - Health check

# Pose Analyzer API

A real-time pose detection and angle calculation API built with FastAPI and MediaPipe. This API provides pose estimation, joint/segment angle calculations, and person tracking capabilities that can be consumed by frontend applications.

## Features

- **Real-time pose detection** using MediaPipe Holistic
- **Joint and segment angle calculations** following biomechanical conventions
- **Multi-person tracking** across frames
- **WebSocket support** for real-time streaming
- **RESTful API** for image and video analysis
- **Filtering and interpolation** for smooth results
- **JSON output format** optimized for frontend visualization

## Installation

### Local Development

1. Clone the repository:

```bash
git clone <your-repo>
cd pose-analyzer-api
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy environment variables:

```bash
cp .env.example .env
```

5. Run the application:

```bash
python -m src.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /api/health
```

### Analyze Single Image

```
POST /api/analyze/image
Content-Type: multipart/form-data
Body: file (image file)
```

### Analyze Video

```
POST /api/analyze/video
Content-Type: multipart/form-data
Body: file (video file)
Query params:
  - start_time (optional): Start time in seconds
  - end_time (optional): End time in seconds
  - skip_frames (optional): Process every Nth frame
```

### Get Angle Definitions

```
GET /api/angles/definitions
```

### WebSocket Streaming

```
WS /ws
Send: Image blob
Receive: JSON pose data
```

## Usage Examples

### Python Client

```python
import requests

# Analyze image
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze/image',
        files={'file': f}
    )
    result = response.json()
```

### JavaScript/React Client

```javascript
// See examples/api_client_example.js for complete React examples

// Analyze image
const formData = new FormData();
formData.append("file", imageFile);

const response = await fetch("http://localhost:8000/api/analyze/image", {
  method: "POST",
  body: formData,
});

const result = await response.json();
```

## JSON Output Format

```json
{
  "frame_id": 0,
  "timestamp": 0.033,
  "processing_time_ms": 15.2,
  "persons": [
    {
      "person_id": 0,
      "tracking_confidence": 0.95,
      "keypoints": {
        "nose": { "x": 320, "y": 240, "confidence": 0.98 },
        "left_shoulder": { "x": 300, "y": 280, "confidence": 0.95 }
        // ... all keypoints
      },
      "angles": {
        "joint_angles": {
          "right_knee": 145.2,
          "left_knee": 142.8
          // ... all joint angles
        },
        "segment_angles": {
          "right_thigh": 85.3,
          "trunk": 92.1
          // ... all segment angles
        }
      },
      "metrics": {
        "height_pixels": 450,
        "center_of_mass": { "x": 320, "y": 350 },
        "velocity": { "x": 2.5, "y": 0.1 },
        "visible_side": "right",
        "movement_direction": "left_to_right"
      }
    }
  ],
  "frame_metrics": {
    "detected_persons": 1,
    "average_confidence": 0.89,
    "processing_fps": 65
  }
}
```

## Local Demo

Run the demo script to test with webcam or video file:

```bash
# Webcam
python examples/demo_video.py --webcam

# Video file
python examples/demo_video.py --video sample.mp4

# Video with angle plots
python examples/demo_video.py --video sample.mp4 --plot
```

## Deployment to Google Cloud

### Using App Engine

1. Install Google Cloud SDK

2. Initialize your project:

```bash
gcloud init
gcloud app create
```

3. Deploy:

```bash
gcloud app deploy
```

### Using Cloud Run

1. Build container:

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/pose-analyzer .
```

2. Push to Container Registry:

```bash
docker push gcr.io/YOUR_PROJECT_ID/pose-analyzer
```

3. Deploy to Cloud Run:

```bash
gcloud run deploy pose-analyzer \
  --image gcr.io/YOUR_PROJECT_ID/pose-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

Edit `.env` file to configure:

- `PORT`: API port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins
- `MAX_UPLOAD_SIZE_MB`: Maximum file upload size
- `CONFIDENCE_THRESHOLD`: Minimum pose detection confidence

## Features Inherited from Sports2D

- **Person Detection & Tracking**: Multi-person tracking with consistent IDs
- **Angle Calculations**: Joint and segment angles with biomechanical conventions
- **Data Processing**: Interpolation and filtering (Butterworth, Gaussian, Median)
- **Quality Metrics**: Confidence scores and tracking metrics
- **Coordinate Systems**: Automatic side detection and orientation

## License

MIT License

o Run Locally:

Setup:

bashpip install -r requirements.txt
cp .env.example .env

Run API:

bashpython -m src.main

Test with Demo:

bash# Test with webcam
python examples/demo_video.py --webcam

# Test with video

python examples/demo_video.py --video sample.mp4
To Deploy to Google Cloud:

App Engine:

bashgcloud app deploy

Cloud Run (recommended for WebSocket support):

bashdocker build -t gcr.io/YOUR_PROJECT_ID/pose-analyzer .
docker push gcr.io/YOUR_PROJECT_ID/pose-analyzer
gcloud run deploy pose-analyzer --image gcr.io/YOUR_PROJECT_ID/pose-analyzer
React Integration:
The examples/api_client_example.js file shows how to:

Upload and analyze images/videos
Set up WebSocket streaming
Display pose skeleton and angles
Handle real-time updates

Next Steps:

Phase 2: Add more pose models (RTMPose, OpenPose)
Phase 3: Add sports-specific analysis
Phase 4: Implement calibration and 3D conversion
