from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AnalysisResponse(BaseModel):
    """Response model for video analysis"""
    analysis_id: str
    status: str
    message: str
    file_name: Optional[str] = None

class DetectedObject(BaseModel):
    """Model for a detected object"""
    id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    frame_number: int

class AnalysisResult(BaseModel):
    """Model for analysis results"""
    analysis_id: str
    total_frames: int
    fps: float
    duration: float
    detections: List[DetectedObject]
    summary: Dict[str, Any]