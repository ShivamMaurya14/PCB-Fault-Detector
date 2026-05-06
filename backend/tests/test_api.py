import pytest
from fastapi.testclient import TestClient
from backend.api import app
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY", "my-secure-api-key")

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_detect_no_auth():
    response = client.post("/detect", files={"file": ("test.jpg", b"fake-image-bytes", "image/jpeg")})
    assert response.status_code == 403
    assert response.json()["detail"] == "Could not validate credentials"

def test_detect_invalid_file_type():
    headers = {"X-API-Key": API_KEY}
    response = client.post("/detect", headers=headers, files={"file": ("test.txt", b"text", "text/plain")})
    assert response.status_code == 400
    assert response.json()["detail"] == "File provided is not an image."

# Testing the actual detection with mock mode
def test_detect_valid_image():
    # Create a dummy image
    import cv2
    import numpy as np
    
    # create a small blank image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    assert success
    
    headers = {"X-API-Key": API_KEY}
    response = client.post(
        "/detect", 
        headers=headers, 
        files={"file": ("dummy.jpg", encoded_image.tobytes(), "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_defective" in data
    assert "defects" in data
    assert "inference_time_ms" in data
