# Default to standard slim python for broad compatibility during dev.
# ---> FOR JETSON DEPLOYMENT, CHANGE TO: FROM nvcr.io/nvidia/l4t-tensorrt:r35.2.1
# or nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3 depending on your base needs
FROM python:3.10-slim

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install them
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the application structure
COPY backend/ ./backend/
COPY model/ ./model/

# Expose FastAPI and OPC-UA ports
EXPOSE 8000
EXPOSE 4840

# Run the orchestrator
ENV PYTHONPATH=/app
CMD ["python", "-m", "backend.main"]
