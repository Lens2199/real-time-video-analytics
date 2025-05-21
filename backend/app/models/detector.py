import logging
import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from typing import List, Dict, Any, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class ObjectDetector:
    """
    YOLOv8 object detector class
    """
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        """
        Initialize the object detector
        
        Args:
            model_path (str): Path to the YOLOv8 model file (.pt)
            confidence_threshold (float): Minimum confidence threshold for detections
        """
        self.confidence_threshold = confidence_threshold
        
        # Load the model with safe globals
        try:
            logger.info(f"Loading YOLOv8 model from {model_path}")
            
            # Add safe globals for YOLOv8 model loading
            torch.serialization.add_safe_globals([
                'ultralytics.nn.tasks.DetectionModel',
                'ultralytics.nn.modules.conv.Conv',
                'ultralytics.nn.modules.block.C2f',
                'ultralytics.nn.modules.head.Detect',
                'ultralytics.models.yolo.detect.DetectionPredictor',
                'ultralytics.models.yolo.detect.DetectionValidator',
                'ultralytics.models.yolo.detect.DetectionTrainer'
            ])
            
            self.model = YOLO(model_path)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise e
        
        # Get class names
        self.class_names = self.model.names
        
        logger.info(f"Model initialized with {len(self.class_names)} classes")

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect objects in a frame
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            List[Dict[str, Any]]: List of detection results
        """
        try:
            # Run inference
            results = self.model(frame, verbose=False)[0]
            
            # Process results
            detections = []
            
            for i, det in enumerate(results.boxes.data.tolist()):
                # Format: [x1, y1, x2, y2, confidence, class_id]
                x1, y1, x2, y2, conf, class_id = det
                
                # Skip if confidence is below threshold
                if conf < self.confidence_threshold:
                    continue
                
                # Convert class_id to integer
                class_id = int(class_id)
                
                # Get class name
                class_name = self.class_names[class_id]
                
                # Add detection to list
                detections.append({
                    "id": i,
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during object detection: {str(e)}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw detection boxes and labels on frame
        
        Args:
            frame (np.ndarray): Input frame
            detections (List[Dict[str, Any]]): List of detection results
            
        Returns:
            np.ndarray: Frame with detections drawn
        """
        # Make a copy of the frame
        output_frame = frame.copy()
        
        # Define colors for different classes (for up to 80 classes)
        colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0), 
                  (0, 255, 255), (255, 0, 255), (128, 0, 0), (0, 128, 0)]
        
        # Draw each detection
        for det in detections:
            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, det["bbox"])
            
            # Get class ID and color
            class_id = det["class_id"] % len(colors)
            color = colors[class_id]
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label text
            label = f"{det['class_name']}: {det['confidence']:.2f}"
            
            # Get label size
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            
            # Draw label background
            cv2.rectangle(
                output_frame, 
                (x1, y1 - text_height - 5), 
                (x1 + text_width, y1), 
                color, 
                -1
            )
            
            # Draw label text
            cv2.putText(
                output_frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
        
        return output_frame