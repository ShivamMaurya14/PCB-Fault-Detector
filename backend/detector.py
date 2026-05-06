import os
import cv2
import numpy as np
import random
from ultralytics import YOLO

class PCBDetector:
    def __init__(self, model_path=None):
        if model_path is None:
            # Safely resolve model path relative to project root
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(root_dir, "model", "best.engine")
        self.classes = [
            "Missing_hole", 
            "Mouse_bite", 
            "Open_circuit", 
            "Short_circuit", 
            "Spur", 
            "Spurious_copper"
        ]
        self.use_mock = True
        self.model = None
        
        # In a real environment, load the TensorRT or PyTorch model
        if os.path.exists(model_path):
            try:
                self.model = YOLO(model_path, task='detect')
                self.use_mock = False
                print(f"Loaded model from {model_path}")
            except Exception as e:
                print(f"Failed to load model from {model_path}: {e}. Falling back to mock.")
        else:
            print(f"Model not found at {model_path}. Running in MOCK mode.")

    def detect(self, image_bytes: bytes):
        """
        Runs detection on the input image bytes.
        Returns a list of detected defects and their bounding boxes.
        """
        # Convert bytes to numpy array then to OpenCV image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Invalid image provided")

        if not self.use_mock and self.model is not None:
            # Real inference
            results = self.model(img, conf=0.25)[0]
            detections = []
            for box in results.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].tolist()
                detections.append({
                    "class_name": self.classes[cls_id],
                    "confidence": conf,
                    "bbox": xyxy
                })
            return detections
        else:
            # Mock inference
            # 50% chance of returning a random defect for demonstration
            detections = []
            if random.random() > 0.5:
                num_defects = random.randint(1, 3)
                height, width = img.shape[:2]
                for _ in range(num_defects):
                    cls_name = random.choice(self.classes)
                    x1 = random.randint(0, width // 2)
                    y1 = random.randint(0, height // 2)
                    x2 = random.randint(x1 + 10, width)
                    y2 = random.randint(y1 + 10, height)
                    
                    detections.append({
                        "class_name": cls_name,
                        "confidence": round(random.uniform(0.5, 0.99), 2),
                        "bbox": [x1, y1, x2, y2]
                    })
            return detections
