import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.violation import Violation
from app.models.delivery_log import DeliveryLog
from app.models.gate_entry import GateEntry
from app.ai.zone_geometry import is_point_in_polygon
from app.ai.ppe_detector import analyze_person_ppe
from app.ai.vehicle_counter import GateVehicleCounter

class SiteIntelligencePipeline:
    """
    AI Computer Vision Pipeline orchestrator.
    Processes video stream frames, performs PPE detection, restricted zone polygon checks,
    gate vehicle counting, and persists violation audit entries into PostgreSQL.
    """
    def __init__(self, gate_id: Optional[uuid.UUID] = None, zone_id: Optional[uuid.UUID] = None):
        self.gate_id = gate_id
        self.zone_id = zone_id
        self.vehicle_counter = GateVehicleCounter(gate_id=str(gate_id) if gate_id else "gate-01")

    def process_frame_detections(
        self,
        db: Session,
        person_detections: List[Dict[str, Any]],
        vehicle_detections: List[Tuple[int, Tuple[int, int, int, int]]],
        restricted_zone_polygon: Optional[List[Tuple[float, float]]] = None
    ) -> Dict[str, Any]:
        """
        Process a single video frame detection payload.
        
        Args:
            db: SQLAlchemy Session instance
            person_detections: List of dicts containing bbox (x1, y1, x2, y2), crop, and optional ppe_override flags
            vehicle_detections: List of tracked vehicles (track_id, bbox)
            restricted_zone_polygon: Optional list of (x, y) vertices for hazardous zone checks
            
        Returns:
            Dict[str, Any]: Processing metrics (logged_violations_count, current_ai_vehicle_count)
        """
        logged_violations = []

        # 1. Process Person Detections (PPE Compliance & Restricted Zone Checks)
        for det in person_detections:
            bbox = det.get("bbox", (0, 0, 100, 100))
            crop = det.get("crop")

            x1, y1, x2, y2 = bbox
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            person_center = (center_x, center_y)

            # A. PPE Compliance Check
            ppe_result = det.get("ppe_override") or analyze_person_ppe(crop, bbox)
            helmet_missing = ppe_result.get("helmet_missing", False)
            vest_missing = ppe_result.get("vest_missing", False)

            passed_ppe = not (helmet_missing or vest_missing)
            
            # Log real GateEntry row in DB for every person detection (pass or fail)
            gate_entry = GateEntry(
                gate_id=self.gate_id,
                passed_ppe=passed_ppe,
                helmet_present=not helmet_missing,
                vest_present=not vest_missing,
                logged_at=datetime.utcnow()
            )
            db.add(gate_entry)

            if helmet_missing or vest_missing:
                violation = Violation(
                    gate_id=self.gate_id,
                    zone_id=self.zone_id,
                    violation_type="ppe_missing",
                    helmet_missing=helmet_missing,
                    vest_missing=vest_missing,
                    image_url=det.get("image_url", "/storage/violations/sample_ppe.jpg"),
                    detected_at=datetime.utcnow()
                )
                db.add(violation)
                logged_violations.append(violation)

            # B. Restricted Hazardous Zone Polygon Check
            if restricted_zone_polygon and is_point_in_polygon(person_center, restricted_zone_polygon):
                zone_violation = Violation(
                    gate_id=self.gate_id,
                    zone_id=self.zone_id,
                    violation_type="restricted_zone_entry",
                    helmet_missing=helmet_missing,
                    vest_missing=vest_missing,
                    image_url=det.get("image_url", "/storage/violations/sample_zone.jpg"),
                    detected_at=datetime.utcnow()
                )
                db.add(zone_violation)
                logged_violations.append(zone_violation)

        # 2. Process Gate Vehicle Count Line Crossing
        current_ai_count = self.vehicle_counter.update_vehicle_tracks(vehicle_detections)

        db.commit()

        return {
            "logged_violations_count": len(logged_violations),
            "current_ai_vehicle_count": current_ai_count,
            "violations": logged_violations
        }
