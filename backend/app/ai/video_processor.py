import os
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
import requests

from app.core.security import create_access_token
from app.ai.ppe_detector import classify_cropped_person_ppe, MIN_CONFIDENCE_THRESHOLD
from app.ai.zone_geometry import is_person_in_restricted_zone
from app.ai.vehicle_counter import GateVehicleCounter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIVideoProcessor")

class VideoStreamProcessor:
    """
    AI Video Processing Pipeline Engine.
    Reads input video files, crops person detections, classifies PPE, checks restricted zones,
    tracks vehicle counts, and posts violations via authenticated HTTP API calls to backend.
    """
    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/api/v1",
        gate_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        service_user_id: Optional[uuid.UUID] = None,
        service_role: str = "admin"
    ):
        self.api_base_url = api_base_url.rstrip("/")
        self.gate_id = gate_id
        self.zone_id = zone_id
        self.vehicle_counter = GateVehicleCounter(gate_id=gate_id or "gate-01")

        # Generate internal service account JWT access token for authenticating API calls
        self.service_token = create_access_token(
            subject=service_user_id or uuid.uuid4(),
            role=service_role
        )

    def _sanitize_filepath(self, filename: str) -> str:
        """
        Sanitizes input filenames/paths before saving to storage to prevent directory traversal vulnerabilities.
        """
        clean_basename = os.path.basename(filename)
        sanitized_name = "".join(c for c in clean_basename if c.isalnum() or c in (".", "_", "-"))
        return f"{uuid.uuid4()}_{sanitized_name}"

    def process_video_file(
        self,
        video_path: str,
        restricted_zone_polygon: Optional[List[Tuple[float, float]]] = None,
        simulated_detections_by_frame: Optional[Dict[int, List[Dict[str, Any]]]] = None,
        http_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Reads and processes a video file frame-by-frame.
        
        Args:
            video_path: Path to the input video file.
            restricted_zone_polygon: Optional polygon vertices for zone breach detection.
            simulated_detections_by_frame: Optional frame-indexed detection frames for testing/demo.
            http_client: Optional custom HTTP client or TestClient instance.
            
        Returns:
            Dict[str, Any]: Execution report metrics (total_frames, violations_logged, ai_vehicle_count, status).
        """
        # 1. Input Video Validation & File Reading
        if not os.path.exists(video_path):
            logger.error(f"Video file not found at path: {video_path}")
            return {"status": "error", "message": f"Video file not found: {video_path}", "violations_logged": 0}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Corrupted or unreadable video file: {video_path}")
            return {"status": "error", "message": "Corrupted or unreadable video file", "violations_logged": 0}

        frame_count = 0
        violations_logged = 0

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                frame_count += 1

                # Extract detections for this frame (or simulated model output)
                frame_dets = (simulated_detections_by_frame or {}).get(frame_count, [])

                for det in frame_dets:
                    bbox = det.get("bbox", (10, 10, 100, 200))
                    confidence = det.get("confidence", 0.9)
                    
                    # Crop person box
                    x1, y1, x2, y2 = bbox
                    h, w, _ = frame.shape
                    x1_c, y1_c = max(0, x1), max(0, y1)
                    x2_c, y2_c = min(w, x2), min(h, y2)
                    
                    person_crop = frame[y1_c:y2_c, x1_c:x2_c] if (x2_c > x1_c and y2_c > y1_c) else None

                    # A. PPE Detector Two-Stage Classification (with confidence filtering)
                    ppe_eval = classify_cropped_person_ppe(person_crop, confidence, bbox)

                    # Override PPE flags if provided in detection dictionary
                    if "helmet_missing" in det:
                        ppe_eval["helmet_missing"] = det["helmet_missing"]
                    if "vest_missing" in det:
                        ppe_eval["vest_missing"] = det["vest_missing"]

                    # If detection is discarded due to low confidence (< 0.5), skip processing
                    if not ppe_eval["is_valid"]:
                        logger.info(f"Frame {frame_count}: Detection discarded due to low confidence ({confidence:.2f} < 0.5)")
                        continue

                    # B. Check for PPE Violation
                    if ppe_eval["helmet_missing"] or ppe_eval["vest_missing"]:
                        success = self._post_violation_event(
                            violation_type="ppe_missing",
                            helmet_missing=ppe_eval["helmet_missing"],
                            vest_missing=ppe_eval["vest_missing"],
                            image_filename=f"frame_{frame_count}.jpg",
                            http_client=http_client
                        )
                        if success:
                            violations_logged += 1

                    # C. Check for Restricted Hazardous Zone Entry
                    if restricted_zone_polygon and is_person_in_restricted_zone(bbox, restricted_zone_polygon):
                        success = self._post_violation_event(
                            violation_type="restricted_zone_entry",
                            helmet_missing=ppe_eval["helmet_missing"],
                            vest_missing=ppe_eval["vest_missing"],
                            image_filename=f"frame_{frame_count}.jpg",
                            http_client=http_client
                        )
                        if success:
                            violations_logged += 1

                # Track vehicles if present in frame
                vehicles_in_frame = [d["track_info"] for d in frame_dets if "track_info" in d]
                if vehicles_in_frame:
                    self.vehicle_counter.update_vehicle_tracks(vehicles_in_frame)

        finally:
            cap.release()

        logger.info(f"Completed processing video file '{video_path}'. Total frames: {frame_count}, Violations logged: {violations_logged}")
        return {
            "status": "success",
            "total_frames": frame_count,
            "violations_logged": violations_logged,
            "ai_vehicle_count": self.vehicle_counter.total_count
        }

    def _post_violation_event(
        self,
        violation_type: str,
        helmet_missing: bool,
        vest_missing: bool,
        image_filename: str,
        http_client: Optional[Any] = None
    ) -> bool:
        """
        Sends an authenticated HTTP request to the backend REST API endpoint POST /api/v1/violations.
        """
        sanitized_filename = self._sanitize_filepath(image_filename)
        headers = {
            "Authorization": f"Bearer {self.service_token}",
            "Content-Type": "application/json"
        }
        
        # Internal API call payload
        payload = {
            "gate_id": self.gate_id,
            "zone_id": self.zone_id,
            "violation_type": violation_type,
            "helmet_missing": helmet_missing,
            "vest_missing": vest_missing,
            "image_url": f"/storage/violations/{sanitized_filename}"
        }

        # Send request via TestClient or live HTTP requests
        if http_client is not None:
            res = http_client.post("/api/v1/violations/internal", headers=headers, json=payload)
            return res.status_code in (200, 201)
        else:
            try:
                res = requests.post(f"{self.api_base_url}/violations/internal", headers=headers, json=payload, timeout=5)
                return res.status_code in (200, 201)
            except Exception as e:
                logger.error(f"Failed to post violation event over HTTP: {e}")
                return False
