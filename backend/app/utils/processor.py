import os
import cv2
import logging
import tempfile
import time
import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from app.models.detector import ObjectDetector
from app.models.tracker import ObjectTracker
from app.agents.coordinator import CoordinatorAgent
from app.config import RESULTS_DIR

# Set up logging
logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Video processing class for AI analysis
    """
    def __init__(self, use_agents=True):
        """
        Initialize the video processor
        
        Args:
            use_agents (bool): Whether to use the multi-agent system
        """
        self.use_agents = use_agents
        
        if use_agents:
            # Initialize multi-agent system
            self.coordinator = CoordinatorAgent("coordinator_1")
        else:
            # Initialize direct detector and tracker
            self.detector = ObjectDetector()
            self.tracker = ObjectTracker()
        
        # Dictionary to store processing status for each analysis
        self.processing_status = {}
        
        # Dictionary to store detection results
        self.detection_results = {}
        
        # Create results directory if it doesn't exist
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        logger.info(f"Video processor initialized with multi-agent system: {use_agents}")
    
    async def process_video(self, video_path: str, analysis_id: str, 
                      detection_interval: int = 15, save_output: bool = True):
        """
        Process a video file for object detection and tracking (simplified without socket.io)
        
        Args:
            video_path (str): Path to the input video file
            analysis_id (str): Unique ID for this analysis
            detection_interval (int): Interval between detections (in frames)
            save_output (bool): Whether to save the output video
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Update status
            self.processing_status[analysis_id] = {
                "status": "processing", 
                "progress": 0,
                "message": "Starting video processing"
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
            
            # Set up video writer for output video (if requested)
            output_video_path = None
            out = None
            
            if save_output:
                # Create output file path
                output_video_path = os.path.join(RESULTS_DIR, f"{analysis_id}_output.mp4")
                
                # Initialize video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
            
            # Initialize results
            all_detections = []
            frame_count = 0
            processing_time = 0
            
            # Reset coordinator statistics if using agents
            if self.use_agents:
                self.coordinator.reset_statistics()
            
            # Process each frame
            while True:
                # Read frame
                ret, frame = cap.read()
                
                # Break if end of video
                if not ret:
                    break
                
                start_time = time.time()
                
                # Process the frame
                if self.use_agents:
                    # Use multi-agent system
                    result = self.coordinator.process(frame)
                    
                    # Extract detections and tracks
                    detections = result.get("detections", [])
                    tracks = result.get("tracks", [])
                    
                    # Combine detections and tracks
                    combined_objects = detections + tracks
                    
                    # Add frame number to objects
                    for obj in combined_objects:
                        obj["frame_number"] = frame_count
                    
                    # Add to all detections
                    all_detections.extend(combined_objects)
                    
                    # Draw objects on the frame (use the detection agent for this)
                    if combined_objects:
                        frame = self.coordinator.detection_agent.detector.draw_detections(frame, combined_objects)
                else:
                    # Use detector directly at intervals
                    if frame_count % detection_interval == 0 or frame_count == 0:
                        # Detect objects
                        detections = self.detector.detect(frame)
                        
                        # Initialize or reinitialize the tracker
                        if self.tracker and detections:
                            self.tracker.reinitialize(frame, detections)
                        
                        # Add frame number to detections
                        for det in detections:
                            det["frame_number"] = frame_count
                        
                        # Add to all detections
                        all_detections.extend(detections)
                    
                    # Otherwise, use tracker to update object positions
                    elif self.tracker:
                        tracking_results = self.tracker.update(frame)
                        
                        # Add frame number to detections
                        for det in tracking_results:
                            det["frame_number"] = frame_count
                        
                        # Add to all detections
                        all_detections.extend(tracking_results)
                    
                    # Draw detections on the frame
                    if all_detections:
                        # Filter detections for the current frame
                        current_detections = [d for d in all_detections if d["frame_number"] == frame_count]
                        frame = self.detector.draw_detections(frame, current_detections)
                
                # Write frame to output video
                if out is not None:
                    out.write(frame)
                
                # Calculate processing time
                processing_time += time.time() - start_time
                
                # Update progress every 10 frames
                if frame_count % 10 == 0:
                    progress = min(100, int((frame_count / total_frames) * 100))
                    
                    # Update status
                    self.processing_status[analysis_id] = {
                        "status": "processing",
                        "progress": progress,
                        "message": f"Processing frame {frame_count}/{total_frames}"
                    }
                
                # Increment frame counter
                frame_count += 1
            
            # Get statistics
            if self.use_agents:
                # Get statistics from coordinator
                agent_stats = self.coordinator.get_statistics()
                class_counts = agent_stats["detection_classes"]
                total_detections = agent_stats["total_detections"]
                avg_processing_time = agent_stats["avg_processing_time"]
            else:
                # Calculate statistics manually
                class_counts = {}
                
                for det in all_detections:
                    class_name = det["class_name"]
                    if class_name in class_counts:
                        class_counts[class_name] += 1
                    else:
                        class_counts[class_name] = 1
                
                total_detections = len(all_detections)
                avg_processing_time = processing_time / frame_count if frame_count > 0 else 0
            
            # Prepare results
            results = {
                "analysis_id": analysis_id,
                "total_frames": total_frames,
                "processed_frames": frame_count,
                "fps": fps,
                "duration": total_frames / fps if fps > 0 else 0,
                "avg_processing_time": avg_processing_time,
                "output_video": output_video_path,
                "detections": all_detections,
                "summary": {
                    "total_detections": total_detections,
                    "class_counts": class_counts
                }
            }
            
            # Save results to file
            results_file_path = os.path.join(RESULTS_DIR, f"{analysis_id}_results.json")
            
            with open(results_file_path, 'w') as f:
                # Convert detections to serializable format
                serializable_results = results.copy()
                serializable_results["detections"] = [
                    {k: v for k, v in det.items() if k != "tracker"}
                    for det in all_detections
                ]
                
                json.dump(serializable_results, f, indent=2)
            
            # Update status
            self.processing_status[analysis_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Video processing completed",
                "results_file": results_file_path
            }
            
            # Store detection results
            self.detection_results[analysis_id] = results
            
            # Release resources
            cap.release()
            if out is not None:
                out.release()
            
            logger.info(f"Video processing completed: {analysis_id}")
            
            return results
            
        except Exception as e:
            # Update status on error
            self.processing_status[analysis_id] = {
                "status": "error",
                "progress": 0,
                "message": str(e)
            }
            
            logger.error(f"Error processing video: {str(e)}")
            raise e
    
    def get_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the processing status for an analysis
        
        Args:
            analysis_id (str): Analysis ID
            
        Returns:
            Dict[str, Any]: Processing status
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
        
        Args:
            analysis_id (str): Analysis ID
            
        Returns:
            Dict[str, Any]: Analysis results
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