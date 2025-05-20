import os
import logging
import aiofiles
from fastapi import UploadFile
import cv2
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """
    Save an uploaded file to the specified destination
    """
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Save the file
        async with aiofiles.open(destination, 'wb') as out_file:
            content = await upload_file.read()
            await out_file.write(content)
        
        return destination
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise e

def get_video_info(video_path: str) -> dict:
    """
    Get basic information about a video file
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")
        
        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Release the video capture object
        cap.release()
        
        return {
            "frame_count": frame_count,
            "fps": fps,
            "width": width,
            "height": height,
            "duration": duration
        }
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        raise e

def extract_frame(video_path: str, frame_number: int) -> np.ndarray:
    """
    Extract a specific frame from a video
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")
        
        # Set the position of the video file to the specified frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read the frame
        ret, frame = cap.read()
        
        # Release the video capture object
        cap.release()
        
        if not ret:
            raise Exception(f"Could not read frame {frame_number} from video")
        
        return frame
    except Exception as e:
        logger.error(f"Error extracting frame: {str(e)}")
        raise e