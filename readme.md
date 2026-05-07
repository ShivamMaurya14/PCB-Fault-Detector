# Real-Time PCB Faults Detection (Edge & Industry 4.0)

<div align="center">
  <img src="https://img.shields.io/badge/YOLO-v11-blue.svg" alt="YOLOv11">
  <img src="https://img.shields.io/badge/Hardware-NVIDIA%20Jetson%20Orin-76B900.svg" alt="Jetson">
  <img src="https://img.shields.io/badge/API-FastAPI-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Protocol-OPC--UA-orange.svg" alt="OPC-UA">
  <img src="https://img.shields.io/badge/Telemetry-Grafana-F46800.svg" alt="Grafana">
</div>

## 📌 Overview
This project implements an automated, high-performance object detection pipeline designed for **Industry 4.0 factory floors**. It identifies and localizes manufacturing defects on Printed Circuit Boards (PCBs) in real-time. 

Built specifically for **Edge Deployment**, it leverages the **YOLOv11s** architecture running on **NVIDIA Jetson Orin NX** via **TensorRT**, achieving 60+ FPS inference. The system integrates a fully secured REST API, an industrial OPC-UA server, and an automated Grafana telemetry stack to prove on-device inference claims with real hardware numbers.

## 🏭 Defect Classes
Trained on the **PKU-Market-PCB** dataset, the system detects 6 common defects:
1. `Missing_hole`
2. `Mouse_bite`
3. `Open_circuit`
4. `Short_circuit`
5. `Spur`
6. `Spurious_copper`

## 🚀 Key Features
- **High-Speed Edge Inference:** Optimized via TensorRT (`.engine`) for Jetson Orin NX. Features a robust wrapper with graceful "Mock Mode" fallback for development without GPU hardware.
- **Industry 4.0 Telemetry (OPC-UA):** Exposes real-time production metrics (e.g., `Total_Defective_PCBs`, `Last_Defect_Type`) securely via an authenticated OPC-UA server.
- **Automated Dashboarding:** Pre-provisioned **Grafana**, **InfluxDB**, and **Telegraf** Docker stack that instantly visualizes defect rates—zero manual configuration required.
- **Traceability & QC Logging:** Automatically draws bounding boxes on defective boards and archives the annotated images locally for Quality Control review.
- **Secure Architecture:** Implements `X-API-Key` authentication for the FastAPI REST endpoints and Username/Password authentication for the OPC-UA nodes.

## 🏗️ Project Architecture
```text
.
├── backend/
│   ├── api.py              # Secured FastAPI REST application
│   ├── camera_client.py    # Edge script to capture & stream CSI/USB video
│   ├── detector.py         # YOLOv11 TensorRT Inference wrapper
│   ├── opcua_server.py     # Authenticated async OPC-UA server
│   ├── main.py             # Asyncio orchestrator for API & OPC-UA
│   └── tests/              # Pytest automated test suite
├── docker-compose.yml      # Multi-container telemetry stack (API, InfluxDB, Grafana)
├── Dockerfile              # Jetson-ready Python container definition
├── grafana/                # Pre-configured Dashboards and Data Sources
├── model/                  # Directory for best.engine weights
├── notebook/               # Model training, evaluation, and TensorRT export pipeline
└── telegraf/               # OPC-UA to InfluxDB bridge configuration
```

## ⚙️ Quick Start Guide

### 1. Environment Setup
Configure your environment variables by checking the `.env` file in the root directory:
```env
API_PORT=8000
API_KEY=my-secure-api-key
OPCUA_PORT=4840
OPCUA_USER=admin
OPCUA_PASSWORD=adminpassword123
CAMERA_SOURCE=0
```

### 2. Launch the Factory Stack (Docker)
Start the entire ecosystem, including the Backend, InfluxDB, Telegraf, and Grafana:
```bash
docker-compose up -d --build
```
*Note: For deployment to physical NVIDIA Jetson hardware, swap the base image in the `Dockerfile` to `nvcr.io/nvidia/l4t-tensorrt`.*

### 3. Simulate the Edge Camera
In a separate terminal, launch the camera client to begin streaming frames to the API:
```bash
# Ensure dependencies are installed locally: pip install -r backend/requirements.txt
python backend/camera_client.py
```

### 4. View the Dashboards
- **Grafana Dashboard:** Navigate to `http://localhost:3000` (Login: `admin` / `admin`). The PCB Defect Monitoring dashboard will be pre-loaded and plotting live data.
- **REST API Docs:** Navigate to `http://localhost:8000/docs` to interact with the Swagger UI.
- **QC Archives:** Defective PCB images are automatically saved with timestamps into the `backend/captured_defects/` folder.

## 🧪 Testing
Run the automated test suite to verify security and API integrity:
```bash
pytest backend/tests/test_api.py
```
