from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
import os
import logging
import uuid
from app.utils.video import save_upload_file, get_video_info
from app.utils.processor import VideoProcessor
from app.api.schemas import AnalysisResponse
from app.main import sio
from app.config import UPLOAD_DIR, RESULTS_DIR

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create video processor with multi-agent system
processor = VideoProcessor(use_agents=True)

# Make upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Make results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

# Helper function to get video processor instance
def get_processor():
    return processor

@router.post("/upload", response_model=AnalysisResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    processor: VideoProcessor = Depends(get_processor)
):
    """
    Upload a video file for processing
    """
    try:
        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{analysis_id}_{file.filename}")
        await save_upload_file(file, file_path)
        
        # Start background processing
        background_tasks.add_task(processor.process_video, file_path, analysis_id, socketio=sio)
        
        logger.info(f"Video uploaded: {file_path}")
        
        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "Video uploaded successfully and processing started",
            "file_name": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_status(
    analysis_id: str,
    processor: VideoProcessor = Depends(get_processor)
):
    """
    Get the status of a video analysis
    """
    status = processor.get_status(analysis_id)
    
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
    
    return status

@router.get("/results/{analysis_id}")
async def get_results(
    analysis_id: str,
    processor: VideoProcessor = Depends(get_processor)
):
    """
    Get the results of a video analysis
    """
    results = processor.get_results(analysis_id)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Results not found: {analysis_id}")
    
    return results

@router.get("/video/{analysis_id}")
async def get_video(analysis_id: str):
    """
    Get the processed video
    """
    video_path = os.path.join(RESULTS_DIR, f"{analysis_id}_output.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Processed video not found: {analysis_id}")
    
    return FileResponse(video_path)

@router.get("/system-info")
async def get_system_info(
    processor: VideoProcessor = Depends(get_processor)
):
    """
    Get information about the video processing system
    """
    info = {
        "system": "AI Video Analysis System",
        "version": "1.0.0",
        "features": {
            "object_detection": True,
            "object_tracking": True,
            "multi_agent_system": processor.use_agents
        },
        "models": {
            "detector": "YOLOv8n",
            "tracker": "KCF"
        }
    }
    
    return info