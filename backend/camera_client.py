import cv2
import requests
import time
import os

import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/detect")
API_KEY = os.getenv("API_KEY", "my-secure-api-key")

# Use 0 for default USB camera.
# On a Jetson device, you might use a GStreamer pipeline string for CSI cameras.
# Example Jetson CSI string:
# CAMERA_SOURCE = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1920, height=1080, format=NV12, framerate=60/1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")
try:
    CAMERA_SOURCE = int(CAMERA_SOURCE)
except ValueError:
    pass 

# Camera Client Configuration
MAX_FPS = int(os.getenv("MAX_FPS", "10"))
frame_delay = 1.0 / MAX_FPS if MAX_FPS > 0 else 0

def main():
    print(f"Connecting to camera: {CAMERA_SOURCE}")
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print(f"Streaming to API: {API_URL} (Target: {MAX_FPS} FPS)")
    print("Press 'q' to quit.")

    consecutive_errors = 0

    while True:
        loop_start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
            
        # Encode frame as JPEG to send over HTTP
        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            continue
            
        # Send to API
        files = {
            'file': ('frame.jpg', encoded_image.tobytes(), 'image/jpeg')
        }
        headers = {
            'X-API-Key': API_KEY
        }
        
        try:
            req_start = time.time()
            response = requests.post(API_URL, files=files, headers=headers, timeout=5.0)
            latency = (time.time() - req_start) * 1000
            
            if response.status_code == 200:
                consecutive_errors = 0 # reset on success
                result = response.json()
                is_defective = result.get('is_defective', False)
                inference_time = result.get('inference_time_ms', 0)
                
                status_text = "DEFECT" if is_defective else "PASS"
                color = (0, 0, 255) if is_defective else (0, 255, 0)
                
                # Draw results on frame for visualization
                if is_defective:
                    for defect in result.get('defects', []):
                        bbox = defect['bbox']
                        cls_name = defect['class_name']
                        x1, y1, x2, y2 = map(int, bbox)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, cls_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                print(f"[{status_text}] Net Latency: {latency:.1f}ms | Inference: {inference_time:.1f}ms")
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                consecutive_errors += 1
                
        except requests.exceptions.RequestException as e:
            print(f"Connection failed: {e}")
            consecutive_errors += 1
            
        # If API is down or failing, back off exponentially up to 5 seconds
        if consecutive_errors > 0:
            backoff = min(5.0, 0.5 * (2 ** (consecutive_errors - 1)))
            print(f"Backing off for {backoff:.1f}s...")
            time.sleep(backoff)

        # Show the live feed locally
        cv2.imshow('Edge Camera Feed', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        # FPS Limiter
        elapsed = time.time() - loop_start
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
