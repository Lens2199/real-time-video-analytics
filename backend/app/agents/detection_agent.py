import logging
import numpy as np
from typing import Dict, List, Any, Optional
from app.agents.base_agent import BaseAgent
from app.models.detector import ObjectDetector

# Set up logging
logger = logging.getLogger(__name__)

class DetectionAgent(BaseAgent):
    """
    Agent for object detection
    """
    def __init__(self, agent_id: str, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the detection agent
        
        Args:
            agent_id (str): Unique ID for this agent
            model_path (str): Path to the YOLOv8 model file
            confidence_threshold (float): Minimum confidence threshold for detections
        """
        super().__init__(agent_id, "detection")
        
        # Initialize the detector
        self.detector = ObjectDetector(model_path, confidence_threshold)
        
        # Store the last detection results
        self.last_detections = []
        self.frame_count = 0
        
        logger.info(f"Initialized detection agent with model: {model_path}")
    
    def process(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Process a frame for object detection
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            List[Dict[str, Any]]: List of detection results
        """
        try:
            # Update frame count
            self.frame_count += 1
            
            # Detect objects
            detections = self.detector.detect(frame)
            
            # Add frame number to detections
            for det in detections:
                det["frame_number"] = self.frame_count
            
            # Store detections
            self.last_detections = detections
            
            # Broadcast detections to connected agents
            if detections:
                self.broadcast("new_detections", {
                    "frame_number": self.frame_count,
                    "detections": detections
                })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return []
    
    def receive_message(self, sender_id: str, message_type: str, content: Any) -> bool:
        """
        Receive a message from another agent
        
        Args:
            sender_id (str): ID of the sender agent
            message_type (str): Type of message
            content (Any): Message content
            
        Returns:
            bool: True if message was processed, False otherwise
        """
        # Handle request_detections message
        if message_type == "request_detections":
            # Find sender agent
            sender = None
            for agent in self.connected_agents:
                if agent.agent_id == sender_id:
                    sender = agent
                    break
            
            if sender:
                # Send last detections to the sender
                sender.receive_message(
                    self.agent_id, 
                    "detection_results", 
                    {
                        "frame_number": self.frame_count,
                        "detections": self.last_detections
                    }
                )
                return True
        
        # Pass to parent class
        return super().receive_message(sender_id, message_type, content)
    
    def draw_detections(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw the last detections on a frame
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            np.ndarray: Frame with detections drawn
        """
        return self.detector.draw_detections(frame, self.last_detections)