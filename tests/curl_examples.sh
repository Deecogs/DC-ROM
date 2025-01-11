# curl_examples.sh
#!/bin/bash

# Test available tests endpoint
curl -X GET "http://localhost:8000/api/v1/available-tests/"

# Configure test
curl -X POST "http://localhost:8000/api/v1/configure-test/" \
     -H "Content-Type: application/json" \
     -d '{"test_type": "hawkins", "include_visualization": true, "save_results": false}'

# Process frame (requires base64 encoded image)
curl -X POST "http://localhost:8000/api/v1/process-frame/" \
     -H "Content-Type: application/json" \
     -d '{"image_data": "BASE64_ENCODED_IMAGE_HERE", "test_type": "hawkins"}'