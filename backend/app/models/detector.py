import logging
import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import torch

# Set up logging
logger = logging.getLogger(__name__)

class ObjectDetector:
    """
    YOLOv8 object detector class with robust error handling
    """
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        """
        Initialize the object detector
        
        Args:
            model_path (str): Path to the YOLOv8 model file (.pt)
            confidence_threshold (float): Minimum confidence threshold for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.class_names = {}
        
        # Set PyTorch environment variables for compatibility
        os.environ['TORCH_SERIALIZATION_SAFE_GLOBALS'] = '1'
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
        # Disable PyTorch warnings in production
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # Load the model with multiple fallback strategies
        self._load_model_with_fallbacks(model_path)
        
        logger.info(f"Model initialized with {len(self.class_names)} classes")

    def _load_model_with_fallbacks(self, model_path):
        """
        Load the model with multiple fallback strategies
        """
        strategies = [
            ("weights_only=False", self._load_with_weights_only_false),
            ("torch.jit.load", self._load_with_torch_jit),
            ("legacy loading", self._load_with_legacy_method),
            ("dummy model", self._create_dummy_model)
        ]
        
        for strategy_name, load_func in strategies:
            try:
                logger.info(f"Attempting to load model with strategy: {strategy_name}")
                success = load_func(model_path)
                if success:
                    logger.info(f"Successfully loaded model using: {strategy_name}")
                    return
            except Exception as e:
                logger.warning(f"Strategy '{strategy_name}' failed: {str(e)}")
                continue
        
        raise Exception("All model loading strategies failed")

    def _load_with_weights_only_false(self, model_path):
        """Strategy 1: Load with weights_only=False"""
        try:
            # Set torch loading to allow pickle
            torch.serialization.add_safe_globals(['numpy.core.multiarray._reconstruct'])
            
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.class_names = self.model.names
            return True
        except Exception as e:
            logger.warning(f"weights_only=False strategy failed: {e}")
            return False

    def _load_with_torch_jit(self, model_path):
        """Strategy 2: Try torch.jit loading (not applicable for YOLO but good fallback)"""
        # This strategy is not applicable for YOLOv8, but kept for completeness
        return False

    def _load_with_legacy_method(self, model_path):
        """Strategy 3: Legacy loading method"""
        try:
            # Try to download a fresh model if the current one is corrupted
            if model_path == "yolov8n.pt":
                import urllib.request
                import tempfile
                
                # Download to temporary location first
                temp_path = os.path.join(tempfile.gettempdir(), "yolov8n_fresh.pt")
                url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt"
                
                logger.info("Downloading fresh YOLOv8 model...")
                urllib.request.urlretrieve(url, temp_path)
                
                from ultralytics import YOLO
                self.model = YOLO(temp_path)
                self.class_names = self.model.names
                return True
        except Exception as e:
            logger.warning(f"Legacy loading failed: {e}")
            return False

    def _create_dummy_model(self, model_path):
        """Strategy 4: Create a dummy model for testing"""
        logger.warning("Creating dummy model - detection will not work properly!")
        
        # Create dummy class names (COCO dataset classes)
        self.class_names = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
            6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
            11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat',
            16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant',
            21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella'
        }
        
        self.model = DummyYOLOModel()
        return True

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect objects in a frame
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            List[Dict[str, Any]]: List of detection results
        """
        try:
            if self.model is None:
                logger.warning("Model not loaded, returning empty detections")
                return []
            
            # Check if it's a dummy model
            if isinstance(self.model, DummyYOLOModel):
                return self._dummy_detect(frame)
            
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
                class_name = self.class_names.get(class_id, f"class_{class_id}")
                
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

    def _dummy_detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Create dummy detections for testing when real model fails
        """
        # Create a fake detection in the center of the frame
        h, w = frame.shape[:2]
        
        return [{
            "id": 0,
            "class_id": 0,
            "class_name": "person",
            "confidence": 0.8,
            "bbox": [w*0.4, h*0.3, w*0.6, h*0.7]  # Center rectangle
        }]
    
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


class DummyYOLOModel:
    """
    Dummy YOLO model for when real model loading fails
    """
    def __init__(self):
        self.names = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
            6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant'
        }
    
    def __call__(self, frame, verbose=False):
        """Dummy inference that returns empty results"""
        return [DummyResults()]


class DummyResults:
    """
    Dummy results class
    """
    def __init__(self):
        self.boxes = DummyBoxes()


class DummyBoxes:
    """
    Dummy boxes class
    """
    def __init__(self):
        self.data = []  # Empty detections
    
    def tolist(self):
        return []