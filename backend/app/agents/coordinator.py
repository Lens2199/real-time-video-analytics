import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional
from app.agents.base_agent import BaseAgent
from app.agents.detection_agent import DetectionAgent
from app.agents.tracking_agent import TrackingAgent

# Set up logging
logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """
    Agent for coordinating the multi-agent system
    """
    def __init__(self, agent_id: str):
        """
        Initialize the coordinator agent
        
        Args:
            agent_id (str): Unique ID for this agent
        """
        super().__init__(agent_id, "coordinator")
        
        # Create sub-agents
        self.detection_agent = DetectionAgent("detection_1")
        self.tracking_agent = TrackingAgent("tracking_1")
        
        # Connect agents
        self.connect(self.detection_agent)
        self.connect(self.tracking_agent)
        self.detection_agent.connect(self.tracking_agent)
        
        # Initialize statistics
        self.stats = {
            "frames_processed": 0,
            "total_detections": 0,
            "total_tracks": 0,
            "processing_time": 0,
            "start_time": 0,
            "detection_classes": {}
        }
        
        # Store current frame
        self.current_frame = None
        
        logger.info("Initialized coordinator agent with detection and tracking agents")
    
    def process(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a frame using the multi-agent system
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            # Store current frame
            self.current_frame = frame
            self.detection_agent.current_frame = frame
            self.tracking_agent.current_frame = frame
            
            # Start timing
            start_time = time.time()
            
            # Process with detection agent every 15 frames or at the beginning
            if self.stats["frames_processed"] % 15 == 0 or self.stats["frames_processed"] == 0:
                detections = self.detection_agent.process(frame)
                
                # Update statistics
                self.stats["total_detections"] += len(detections)
                
                # Update detection class counts
                for det in detections:
                    class_name = det["class_name"]
                    if class_name in self.stats["detection_classes"]:
                        self.stats["detection_classes"][class_name] += 1
                    else:
                        self.stats["detection_classes"][class_name] = 1
                
                # Track detected objects
                tracks = self.tracking_agent.process(frame)
                self.stats["total_tracks"] += len(tracks)
                
                # Create combined result
                result = {
                    "frame_number": self.stats["frames_processed"],
                    "detections": detections,
                    "tracks": tracks,
                    "processing_time": time.time() - start_time
                }
                
            else:
                # Just update tracking
                tracks = self.tracking_agent.process(frame)
                self.stats["total_tracks"] += len(tracks)
                
                # Create result based on tracking
                result = {
                    "frame_number": self.stats["frames_processed"],
                    "detections": [],  # No new detections
                    "tracks": tracks,
                    "processing_time": time.time() - start_time
                }
            
            # Update statistics
            self.stats["frames_processed"] += 1
            self.stats["processing_time"] += time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error in coordinator process: {str(e)}")
            return {
                "frame_number": self.stats["frames_processed"],
                "detections": [],
                "tracks": [],
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics
        
        Returns:
            Dict[str, Any]: Processing statistics
        """
        avg_processing_time = (
            self.stats["processing_time"] / self.stats["frames_processed"] 
            if self.stats["frames_processed"] > 0 else 0
        )
        
        return {
            "frames_processed": self.stats["frames_processed"],
            "total_detections": self.stats["total_detections"],
            "total_tracks": self.stats["total_tracks"],
            "avg_processing_time": avg_processing_time,
            "detection_classes": self.stats["detection_classes"]
        }
    
    def reset_statistics(self):
        """
        Reset processing statistics
        """
        self.stats = {
            "frames_processed": 0,
            "total_detections": 0,
            "total_tracks": 0,
            "processing_time": 0,
            "start_time": time.time(),
            "detection_classes": {}
        }