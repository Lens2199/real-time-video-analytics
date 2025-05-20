import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Upload directory for video files
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Results directory for processed videos
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# AI model settings
MODEL_SETTINGS = {
    "yolo": {
        "model_path": "yolov8n.pt",  # Will download automatically
        "confidence_threshold": 0.5,
        "classes": None  # Detect all classes (COCO dataset)
    }
}

# Socket.IO settings
SOCKETIO_SETTINGS = {
    "cors_allowed_origins": ["*"],  # For production, change to your frontend URL
}

# API settings
API_SETTINGS = {
    "max_upload_size": 100 * 1024 * 1024,  # 100 MB
}