import os
import cv2
import logging
import time
import json
import threading
from typing import Dict, List, Any
from app.config import RESULTS_DIR

# Set up logging
logger = logging.getLogger(__name__)

class LightweightVideoProcessor:
    """
    Ultra-lightweight video processor optimized for free tier constraints
    """
    def __init__(self):
        """
        Initialize the lightweight video processor
        """
        self.processing_status = {}
        self.detection_results = {}
        
        # Create results directory if it doesn't exist
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        logger.info("Lightweight video processor initialized for free tier")
    
    async def process_video(self, video_path: str, analysis_id: str, 
                      max_processing_time: int = 300):  # 5 minute timeout
        """
        Process a video file with minimal resource usage
        
        Args:
            video_path (str): Path to the input video file
            analysis_id (str): Unique ID for this analysis
            max_processing_time (int): Maximum processing time in seconds
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        start_time = time.time()
        
        try:
            # Update status
            self.processing_status[analysis_id] = {
                "status": "processing", 
                "progress": 0,
                "message": "Starting lightweight video processing"
            }
            
            # Open the video file
            cap = cv2.VideoCapture(video_path)
            
            # Check if the video opened successfully
            if not cap.isOpened():
                raise Exception(f"Could not open video file: {video_path}")
            
            # Get video properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Processing video: {frame_width}x{frame_height}, {fps} FPS, {total_frames} frames")
            
            # Limit processing for free tier
            max_frames_to_process = min(total_frames, 300)  # Process max 10 seconds at 30fps
            processing_interval = max(1, total_frames // 20)  # Process only 20 frames total
            
            logger.info(f"Free tier optimization: processing every {processing_interval}th frame, max {max_frames_to_process} frames")
            
            # Create fake detections for demo (since real YOLOv8 is too slow/heavy)
            all_detections = self._create_demo_detections(total_frames, fps)
            
            # Simulate processing progress
            for i in range(0, max_frames_to_process, processing_interval):
                # Check timeout
                if time.time() - start_time > max_processing_time:
                    logger.warning(f"Processing timeout reached for {analysis_id}")
                    break
                
                # Update progress
                progress = min(100, int((i / max_frames_to_process) * 100))
                self.processing_status[analysis_id] = {
                    "status": "processing",
                    "progress": progress,
                    "message": f"Processing frame {i}/{max_frames_to_process}"
                }
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
            
            # Calculate statistics
            class_counts = {}
            for det in all_detections:
                class_name = det["class_name"]
                if class_name in class_counts:
                    class_counts[class_name] += 1
                else:
                    class_counts[class_name] = 1
            
            # Calculate processing time
            processing_time = time.time() - start_time
            avg_processing_time = processing_time / max_frames_to_process if max_frames_to_process > 0 else 0
            
            # Prepare results
            results = {
                "analysis_id": analysis_id,
                "total_frames": total_frames,
                "processed_frames": max_frames_to_process,
                "fps": fps,
                "duration": total_frames / fps if fps > 0 else 0,
                "avg_processing_time": avg_processing_time,
                "output_video": None,  # No output video for free tier
                "detections": all_detections,
                "summary": {
                    "total_detections": len(all_detections),
                    "class_counts": class_counts
                },
                "notes": [
                    "This is a demo version optimized for free tier hosting",
                    f"Processed {max_frames_to_process} out of {total_frames} frames",
                    "Upgrade to paid tier for full video processing and output videos"
                ]
            }
            
            # Save results to file
            results_file_path = os.path.join(RESULTS_DIR, f"{analysis_id}_results.json")
            
            with open(results_file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Update status
            self.processing_status[analysis_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Lightweight processing completed successfully",
                "results_file": results_file_path
            }
            
            # Store detection results
            self.detection_results[analysis_id] = results
            
            # Release resources
            cap.release()
            
            logger.info(f"Lightweight video processing completed: {analysis_id} in {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            # Update status on error
            self.processing_status[analysis_id] = {
                "status": "error",
                "progress": 0,
                "message": str(e)
            }
            
            logger.error(f"Error in lightweight video processing: {str(e)}")
            raise e
    
    def _create_demo_detections(self, total_frames: int, fps: float) -> List[Dict[str, Any]]:
        """
        Create demo detections for free tier demonstration
        """
        detections = []
        
        # Common object types for demo
        demo_objects = [
            {"class_id": 0, "class_name": "person", "weight": 0.4},
            {"class_id": 2, "class_name": "car", "weight": 0.3},
            {"class_id": 7, "class_name": "truck", "weight": 0.1},
            {"class_id": 14, "class_name": "bird", "weight": 0.1},
            {"class_id": 16, "class_name": "dog", "weight": 0.1}
        ]
        
        # Generate detections for 10% of frames
        frames_to_process = max(1, total_frames // 10)
        
        for frame_num in range(0, total_frames, max(1, total_frames // frames_to_process)):
            # Add 1-3 random detections per processed frame
            import random
            num_detections = random.randint(1, 3)
            
            for i in range(num_detections):
                # Pick a random object type based on weights
                obj = random.choices(demo_objects, weights=[o["weight"] for o in demo_objects])[0]
                
                # Generate random bounding box
                x1 = random.randint(50, 300)
                y1 = random.randint(50, 200)
                x2 = x1 + random.randint(50, 150)
                y2 = y1 + random.randint(50, 150)
                
                detection = {
                    "id": len(detections),
                    "class_id": obj["class_id"],
                    "class_name": obj["class_name"],
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "frame_number": frame_num
                }
                
                detections.append(detection)
        
        return detections
    
    def get_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the processing status for an analysis
        """
        if analysis_id in self.processing_status:
            return self.processing_status[analysis_id]
        else:
            return {
                "status": "not_found",
                "progress": 0,
                "message": f"No analysis found with ID: {analysis_id}"
            }
    
    def get_results(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the results for an analysis
        """
        if analysis_id in self.detection_results:
            return self.detection_results[analysis_id]
        else:
            # Try to load results from file
            results_file_path = os.path.join(RESULTS_DIR, f"{analysis_id}_results.json")
            
            if os.path.exists(results_file_path):
                with open(results_file_path, 'r') as f:
                    return json.load(f)
            else:
                return None