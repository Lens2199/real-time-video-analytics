import logging
import numpy as np
from typing import Dict, List, Any, Optional
from app.agents.base_agent import BaseAgent
from app.models.tracker import ObjectTracker

# Set up logging
logger = logging.getLogger(__name__)

class TrackingAgent(BaseAgent):
    """
    Agent for object tracking
    """
    def __init__(self, agent_id: str, tracker_type: str = "KCF"):
        """
        Initialize the tracking agent
        
        Args:
            agent_id (str): Unique ID for this agent
            tracker_type (str): Type of tracker to use
        """
        super().__init__(agent_id, "tracking")
        
        # Initialize the tracker
        self.tracker = ObjectTracker(tracker_type)
        
        # Store the last tracking results
        self.last_tracks = []
        self.frame_count = 0
        self.initialized = False
        
        logger.info(f"Initialized tracking agent with tracker type: {tracker_type}")
    
    def process(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Process a frame for object tracking
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            List[Dict[str, Any]]: List of tracking results
        """
        try:
            # Update frame count
            self.frame_count += 1
            
            # If not initialized, request detections from a detection agent
            if not self.initialized:
                # Find a detection agent
                detection_agent = None
                for agent in self.connected_agents:
                    if agent.agent_type == "detection":
                        detection_agent = agent
                        break
                
                if detection_agent:
                    # Request detections
                    detection_agent.send_message(
                        self.agent_id, 
                        "request_detections", 
                        {"frame_number": self.frame_count}
                    )
                    
                    # We've requested detections, but we don't have them yet
                    # Return empty tracks for now
                    return []
                else:
                    logger.warning("No detection agent found, tracking will not work properly")
                    return []
            
            # If already initialized, update tracks
            tracking_results = self.tracker.update(frame)
            
            # Add frame number to tracks
            for track in tracking_results:
                track["frame_number"] = self.frame_count
            
            # Store tracks
            self.last_tracks = tracking_results
            
            # Broadcast tracks to connected agents
            if tracking_results:
                self.broadcast("new_tracks", {
                    "frame_number": self.frame_count,
                    "tracks": tracking_results
                })
            
            return tracking_results
            
        except Exception as e:
            logger.error(f"Error during tracking: {str(e)}")
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
        # Handle detection_results message
        if message_type == "detection_results":
            try:
                frame_number = content.get("frame_number", 0)
                detections = content.get("detections", [])
                
                # If we have a recent frame, initialize tracker
                if frame_number >= self.frame_count - 5:
                    # Find sender agent to get the current frame
                    sender = None
                    for agent in self.connected_agents:
                        if agent.agent_id == sender_id:
                            sender = agent
                            break
                    
                    if sender and hasattr(sender, "current_frame"):
                        # Initialize tracker with detections
                        self.tracker.init(sender.current_frame, detections)
                        self.initialized = True
                        logger.info(f"Tracker initialized with {len(detections)} detections")
                        return True
            except Exception as e:
                logger.error(f"Error processing detection results: {str(e)}")
        
        # Handle new_detections message
        elif message_type == "new_detections":
            try:
                frame_number = content.get("frame_number", 0)
                detections = content.get("detections", [])
                
                # If the detection is recent, reinitialize tracker
                if frame_number >= self.frame_count - 2:
                    # Find sender agent to get the current frame
                    sender = None
                    for agent in self.connected_agents:
                        if agent.agent_id == sender_id:
                            sender = agent
                            break
                    
                    if sender and hasattr(sender, "current_frame"):
                        # Reinitialize tracker with new detections
                        self.tracker.reinitialize(sender.current_frame, detections)
                        self.initialized = True
                        logger.debug(f"Tracker reinitialized with {len(detections)} detections")
                        return True
            except Exception as e:
                logger.error(f"Error processing new detections: {str(e)}")
        
        # Pass to parent class
        return super().receive_message(sender_id, message_type, content)