import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ObjectTracker:
    """
    Object tracker using OpenCV's built-in trackers
    """
    def __init__(self, tracker_type="KCF"):
        """
        Initialize the object tracker
        
        Args:
            tracker_type (str): Type of tracker to use
                Options: 'KCF', 'CSRT', 'MOSSE'
        """
        self.tracker_type = tracker_type
        self.trackers = []
        self.tracked_objects = []
        self.next_id = 0
        logger.info(f"Initialized {tracker_type} object tracker")
    
    def _create_tracker(self):
        """
        Create a tracker instance based on the selected tracker type
        
        Returns:
            cv2.Tracker: Tracker instance
        """
        if self.tracker_type == "KCF":
            return cv2.legacy.TrackerKCF_create()
        elif self.tracker_type == "CSRT":
            return cv2.legacy.TrackerCSRT_create()
        elif self.tracker_type == "MOSSE":
            return cv2.legacy.TrackerMOSSE_create()
        else:
            # Default to KCF
            logger.warning(f"Unknown tracker type: {self.tracker_type}, using KCF")
            return cv2.legacy.TrackerKCF_create()
    
    def init(self, frame: np.ndarray, detections: List[Dict[str, Any]]):
        """
        Initialize trackers with new detections
        
        Args:
            frame (np.ndarray): Current frame
            detections (List[Dict[str, Any]]): List of detection results
        """
        # Clear existing trackers
        self.trackers = []
        self.tracked_objects = []
        
        # Initialize new trackers for each detection
        for det in detections:
            # Create a new tracker
            tracker = self._create_tracker()
            
            # Get bounding box
            x1, y1, x2, y2 = det["bbox"]
            bbox = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
            
            # Initialize tracker
            success = tracker.init(frame, bbox)
            
            if success:
                # Create tracked object
                tracked_obj = {
                    "id": self.next_id,
                    "tracker": tracker,
                    "class_id": det["class_id"],
                    "class_name": det["class_name"],
                    "confidence": det["confidence"],
                    "bbox": bbox,
                    "history": [bbox]  # Track position history
                }
                
                # Add to tracked objects
                self.tracked_objects.append(tracked_obj)
                self.next_id += 1
        
        logger.info(f"Initialized {len(self.tracked_objects)} trackers")
    
    def update(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Update trackers with new frame
        
        Args:
            frame (np.ndarray): Current frame
            
        Returns:
            List[Dict[str, Any]]: List of tracking results
        """
        results = []
        
        # Process each tracked object
        for i, obj in enumerate(self.tracked_objects):
            # Update tracker
            success, bbox = obj["tracker"].update(frame)
            
            if success:
                # Update bounding box
                obj["bbox"] = bbox
                
                # Add to history
                obj["history"].append(bbox)
                
                # Keep history at reasonable size
                if len(obj["history"]) > 30:  # About 1 second at 30 FPS
                    obj["history"] = obj["history"][-30:]
                
                # Add to results
                results.append({
                    "id": obj["id"],
                    "class_id": obj["class_id"],
                    "class_name": obj["class_name"],
                    "confidence": obj["confidence"],
                    "bbox": [
                        bbox[0], bbox[1],                    # x1, y1
                        bbox[0] + bbox[2], bbox[1] + bbox[3]  # x2, y2
                    ]
                })
        
        return results
    
    def reinitialize(self, frame: np.ndarray, detections: List[Dict[str, Any]]):
        """
        Re-initialize trackers with new detections (for tracking drift correction)
        
        Args:
            frame (np.ndarray): Current frame
            detections (List[Dict[str, Any]]): List of detection results
        """
        # Just call init (which clears and re-initializes trackers)
        self.init(frame, detections)