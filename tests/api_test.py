# api_test.py
import pytest
from fastapi.testclient import TestClient
from main import app
import cv2
import base64

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ROM Calculator API is running"}

def test_available_tests():
    response = client.get("/api/v1/available-tests/")
    assert response.status_code == 200
    assert "hawkins" in response.json()

def test_process_frame():
    # Read test image
    test_image = cv2.imread("test_data/test_pose.jpg")
    _, buffer = cv2.imencode('.jpg', test_image)
    base64_image = base64.b64encode(buffer).decode('utf-8')
    
    response = client.post(
        "/api/v1/process-frame/",
        json={
            "image_data": base64_image,
            "test_type": "hawkins"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "angles" in result
    assert "joint_positions" in result
    assert "processed_image" in result

def test_configure_test():
    response = client.post(
        "/api/v1/configure-test/",
        json={
            "test_type": "hawkins",
            "include_visualization": True,
            "save_results": False
        }
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"