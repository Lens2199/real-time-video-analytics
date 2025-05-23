from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
import os
import logging
import uuid
import threading
import asyncio
from app.utils.video import save_upload_file, get_video_info
from app.api.schemas import AnalysisResponse
from app.config import UPLOAD_DIR, RESULTS_DIR

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Try lightweight processor first (best for free tier), then fall back to others
processor = None
try:
    from app.utils.lightweight_processor import LightweightVideoProcessor
    processor = LightweightVideoProcessor()
    logger.info("Initialized lightweight video processor (optimized for free tier)")
except Exception as e:
    logger.warning(f"Failed to initialize lightweight processor: {e}")
    try:
        from app.utils.simple_processor import SimpleVideoProcessor
        processor = SimpleVideoProcessor()
        logger.info("Initialized simple video processor as fallback")
    except Exception as e2:
        logger.warning(f"Failed to initialize simple processor: {e2}")
        try:
            from app.utils.processor import VideoProcessor
            processor = VideoProcessor(use_agents=False)  # Disable agents for free tier
            logger.info("Initialized basic video processor")
        except Exception as e3:
            logger.error(f"Failed to initialize any processor: {e3}")
            processor = None

# Make upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Global dictionary to track processing status
processing_jobs = {}

def run_video_processing(video_path: str, analysis_id: str):
    """
    Run video processing in a separate thread to avoid HTTP timeouts
    """
    try:
        logger.info(f"Starting background processing for {analysis_id}")
        
        # Update status to processing
        processing_jobs[analysis_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Processing video in background"
        }
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the processing
        if processor:
            result = loop.run_until_complete(
                processor.process_video(video_path, analysis_id)
            )
            
            # Update status to completed
            processing_jobs[analysis_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Processing completed successfully",
                "result": result
            }
            logger.info(f"Background processing completed for {analysis_id}")
        else:
            raise Exception("No processor available")
            
    except Exception as e:
        logger.error(f"Background processing failed for {analysis_id}: {str(e)}")
        processing_jobs[analysis_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Processing failed: {str(e)}"
        }
    finally:
        # Clean up the video file to save space
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Cleaned up video file: {video_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up video file: {e}")

# Helper function to get video processor instance
def get_processor():
    if processor is None:
        raise HTTPException(status_code=500, detail="Video processor not available")
    return processor

@router.options("/upload")
async def upload_options():
    """Handle CORS preflight for upload endpoint"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/upload", response_model=AnalysisResponse)
async def upload_video(
    file: UploadFile = File(...),
    processor = Depends(get_processor)
):
    """
    Upload a video file for processing (returns immediately, processing happens in background)
    """
    try:
        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Check file size (limit to 25MB for free tier)
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > 25:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large ({file_size_mb:.1f}MB). Please use files smaller than 25MB on the free tier."
            )
        
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{analysis_id}_{file.filename}")
        
        # Write the content we already read
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Initialize status
        processing_jobs[analysis_id] = {
            "status": "queued",
            "progress": 0,
            "message": "Video uploaded, queued for processing"
        }
        
        # Start background processing in a separate thread
        thread = threading.Thread(
            target=run_video_processing,
            args=(file_path, analysis_id),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Video uploaded and queued: {file_path} ({file_size_mb:.1f}MB)")
        
        response_data = {
            "analysis_id": analysis_id,
            "status": "queued",
            "message": f"Video uploaded successfully ({file_size_mb:.1f}MB). Processing will begin shortly.",
            "file_name": file.filename
        }
        
        # Return immediately (don't wait for processing)
        return JSONResponse(
            content=response_data,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_status(analysis_id: str):
    """
    Get the status of a video analysis (fast response)
    """
    try:
        # Check our in-memory status first
        if analysis_id in processing_jobs:
            status_data = processing_jobs[analysis_id].copy()
            
            # Don't include the full result in status response
            if "result" in status_data:
                del status_data["result"]
            
            return JSONResponse(
                content=status_data,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        # Fallback to processor status if available
        if processor:
            status = processor.get_status(analysis_id)
            if status["status"] != "not_found":
                return JSONResponse(
                    content=status,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
        
        # Not found
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{analysis_id}")
async def get_results(analysis_id: str):
    """
    Get the results of a video analysis
    """
    try:
        # Check our in-memory results first
        if analysis_id in processing_jobs and processing_jobs[analysis_id]["status"] == "completed":
            result = processing_jobs[analysis_id].get("result")
            if result:
                return JSONResponse(
                    content=result,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
        
        # Fallback to processor results if available
        if processor:
            results = processor.get_results(analysis_id)
            if results:
                return JSONResponse(
                    content=results,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
        
        # Not found
        raise HTTPException(status_code=404, detail=f"Results not found: {analysis_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video/{analysis_id}")
async def get_video(analysis_id: str):
    """
    Get the processed video
    """
    video_path = os.path.join(RESULTS_DIR, f"{analysis_id}_output.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Processed video not found: {analysis_id}")
    
    return FileResponse(
        video_path,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.get("/system-info")
async def get_system_info():
    """
    Get information about the video processing system
    """
    # Count active jobs
    active_jobs = len([job for job in processing_jobs.values() if job["status"] == "processing"])
    completed_jobs = len([job for job in processing_jobs.values() if job["status"] == "completed"])
    
    # Determine which processor is being used
    processor_type = "none"
    features = {"object_detection": False, "object_tracking": False, "multi_agent_system": False}
    
    if processor:
        if hasattr(processor, 'use_agents'):
            processor_type = "multi-agent" if processor.use_agents else "basic"
            features = {
                "object_detection": True,
                "object_tracking": processor.use_agents,
                "multi_agent_system": processor.use_agents
            }
        else:
            processor_type = "simple"
            features = {"object_detection": True, "object_tracking": False, "multi_agent_system": False}
    
    info = {
        "system": "AI Video Analysis System",
        "version": "1.0.0",
        "processor_type": processor_type,
        "features": features,
        "models": {
            "detector": "YOLOv8n",
            "tracker": "KCF" if processor_type == "multi-agent" else "none"
        },
        "stats": {
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "total_jobs": len(processing_jobs)
        },
        "limits": {
            "max_file_size_mb": 25,
            "processing_timeout_minutes": 10
        }
    }
    
    return JSONResponse(
        content=info,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.delete("/cleanup")
async def cleanup_old_jobs():
    """
    Cleanup old completed jobs to save memory
    """
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not available")
    
    # Keep only the 10 most recent jobs
    if len(processing_jobs) > 10:
        # Sort by completion time and keep recent ones
        sorted_jobs = sorted(
            processing_jobs.items(),
            key=lambda x: x[1].get("completed_at", 0),
            reverse=True
        )
        
        # Keep only the first 10
        new_jobs = dict(sorted_jobs[:10])
        processing_jobs.clear()
        processing_jobs.update(new_jobs)
        
        return {"message": f"Cleaned up old jobs, kept {len(processing_jobs)} recent jobs"}
    
    return {"message": "No cleanup needed"}