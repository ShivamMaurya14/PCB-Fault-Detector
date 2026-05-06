import os
import cv2
import numpy as np
import time
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

from backend.detector import PCBDetector

app = FastAPI(title="PCB Defect Detection API", description="Edge API for real-time PCB inspection")
detector = PCBDetector()

opcua_server = None

API_KEY = os.getenv("API_KEY", "my-secure-api-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

# Ensure captured_defects directory exists
DEFECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captured_defects")
os.makedirs(DEFECTS_DIR, exist_ok=True)

class DefectResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]

class DetectionResponse(BaseModel):
    is_defective: bool
    defects: List[DefectResult]
    inference_time_ms: float

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "mock" if detector.use_mock else "tensorrt"}

@app.post("/detect", response_model=DetectionResponse)
async def detect_pcb(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    image_bytes = await file.read()
    
    start_time = time.time()
    try:
        detections = detector.detect(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
        
    inference_time_ms = (time.time() - start_time) * 1000
    is_defective = len(detections) > 0
    
    # Save annotated image if defective
    if is_defective:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is not None:
            for defect in detections:
                bbox = defect['bbox']
                cls_name = defect['class_name']
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(img, cls_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"defect_{timestamp}.jpg"
            filepath = os.path.join(DEFECTS_DIR, filename)
            cv2.imwrite(filepath, img)

    # Update OPC-UA metrics asynchronously but blockingly within the same loop to ensure thread safety
    if opcua_server is not None:
        await opcua_server.update_metrics(is_defective, detections)
    
    return DetectionResponse(
        is_defective=is_defective,
        defects=detections,
        inference_time_ms=round(inference_time_ms, 2)
    )
