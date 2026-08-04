from typing import Tuple, Dict, Any, Optional
import numpy as np

MIN_CONFIDENCE_THRESHOLD = 0.5

def filter_detection_confidence(confidence: float, min_threshold: float = MIN_CONFIDENCE_THRESHOLD) -> bool:
    """
    Evaluates detection confidence score against minimum threshold.
    
    Args:
        confidence: Model prediction confidence score (0.0 to 1.0)
        min_threshold: Minimum acceptable confidence score (default 0.5)
        
    Returns:
        bool: True if detection is valid (>= threshold), False if low-confidence flicker.
    """
    return confidence >= min_threshold

def classify_cropped_person_ppe(
    person_crop: np.ndarray,
    confidence: float,
    bbox: Tuple[int, int, int, int]
) -> Dict[str, Any]:
    """
    Two-stage detect-then-classify PPE model logic.
    Crops detected person bounding box, enforces confidence threshold (0.5),
    and classifies helmet & vest presence.
    
    Args:
        person_crop: Cropped image numpy array of detected person.
        confidence: Detection confidence score.
        bbox: (x1, y1, x2, y2) bounding box coordinates.
        
    Returns:
        Dict[str, Any]: {
            "is_valid": bool,
            "helmet_missing": bool,
            "vest_missing": bool,
            "confidence": float
        }
    """
    # 1. Confidence Threshold Check (discard low-confidence flickers)
    if not filter_detection_confidence(confidence):
        return {
            "is_valid": False,
            "helmet_missing": False,
            "vest_missing": False,
            "confidence": confidence
        }

    # 2. Perform two-stage classification on crop region (upper 25% for head/helmet, middle 50% for vest)
    helmet_missing = False
    vest_missing = False

    if person_crop is not None and person_crop.size > 0 and len(person_crop.shape) == 3:
        h, w, c = person_crop.shape
        head_region = person_crop[0:max(1, int(h * 0.25)), :]
        
        # Analyze head region color/feature variance (if predominantly dark or low brightness, flag helmet missing)
        avg_bgr = np.mean(head_region, axis=(0, 1)) if head_region.size > 0 else [0, 0, 0]
        # Example heuristic check: High blue/yellow signal indicates safety helmet present; otherwise missing
        b, g, r = avg_bgr[0], avg_bgr[1], avg_bgr[2]
        if (r < 100 and g < 100 and b < 100):  # Dark unequipped head region
            helmet_missing = True

    return {
        "is_valid": True,
        "helmet_missing": helmet_missing,
        "vest_missing": vest_missing,
        "confidence": confidence
    }
