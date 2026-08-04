import os
import sys
import json
import time
import uuid
import cv2
import numpy as np
from datetime import datetime
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

# Core imports
from app.main import app
from app.api.deps import get_db
from app.db.base_class import Base
from app.models import User, UserRole, Violation, DeliveryLog, Zone, Equipment, Gate, GateEntry, AdminNotification
from app.core.security import create_access_token, hash_password
from app.services.discrepancy_service import evaluate_delivery_discrepancy
from tests.test_db_config import engine as test_engine, override_get_db

# Helper to re-establish test DB override
def reset_test_db_override():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

# Import existing phase test routines
from tests.test_auth import (
    test_password_hashing,
    test_jwt_token_generation_and_decoding
)
from tests.test_auth_security import (
    test_admin_vs_supervisor_authorization,
    test_refresh_token_rotation,
    test_login_rate_limiting
)
from tests.test_phase4 import (
    test_unit_discrepancy_service_consecutive_streak,
    test_extra_fields_pydantic_rejection,
    test_discrepancy_edge_case_no_ai_count,
    test_disallowed_file_upload_failure_case,
    test_integration_endpoints_and_auth_failures
)
from tests.test_phase4_additions import test_acknowledge_violation_and_reacknowledge_409_conflict
from tests.test_phase6_ai import (
    test_unit_confidence_threshold_logic,
    test_edge_case_empty_scene_zero_violations,
    test_failure_case_corrupted_unreadable_video,
    test_end_to_end_full_pipeline_demo
)
from tests.test_phase7_advanced import (
    test_integration_three_consecutive_mismatches_escalation,
    test_integration_single_mismatch_no_escalation,
    test_security_supervisor_forbidden_from_admin_escalation_endpoint,
    test_ai_hazard_categorization
)
from tests.test_phase8_security_performance import (
    test_security_jwt_tampering_rejection,
    test_security_sqli_parameterization,
    test_performance_concurrent_dashboard_requests
)

def run_real_pexels_yolo_inference_benchmark():
    print("\n==========================================================================")
    print("  RUNNING REAL UN-MOCKED YOLOv8 INFERENCE ON ALL 5 PEXELS DEMO VIDEO CLIPS ")
    print("==========================================================================")

    model = YOLO("yolov8n.pt")
    demo_clips_dir = os.path.join(os.path.dirname(__file__), "..", "storage", "demo_clips")
    
    clips = [
        "demo_compliant.mp4",
        "demo_vehicle_entry.mp4",
        "demo_no_helmet.mp4",
        "demo_restricted_zone.mp4",
        "demo_low_light_limitation.mp4"
    ]

    for clip in clips:
        clip_path = os.path.join(demo_clips_dir, clip)
        if not os.path.exists(clip_path):
            print(f"⚠️ Warning: Demo clip '{clip}' not found at {clip_path}")
            continue

        cap = cv2.VideoCapture(clip_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0.0

        print(f"\n--- Video Clip: {clip} ({duration:.2f}s, {total_frames} frames, {fps:.1f} FPS) ---")

        # Process sample keyframe (frame 10 or mid-frame)
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(10, max(0, total_frames - 1)))
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            print(f"❌ Failed to read frame from {clip}")
            continue

        t0 = time.time()
        results = model.predict(source=frame, conf=0.3, verbose=False)
        t_infer = (time.time() - t0) * 1000.0

        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                class_name = model.names[cls_id]
                confidence = float(box.conf[0].item())
                xyxy = [round(val, 1) for val in box.xyxy[0].cpu().numpy().tolist()]
                detections.append({
                    "class": class_name,
                    "confidence": round(confidence, 4),
                    "box": xyxy
                })

        print(f"  Inference Speed: {t_infer:.1f} ms | Total Keyframe Detections: {len(detections)}")
        for idx, det in enumerate(detections[:5]):
            print(f"    [{idx+1}] Class: {det['class']:12s} | Conf: {det['confidence']:.4f} | Box: {det['box']}")

def run_end_to_end_sequential_master_scenario():
    print("\n==========================================================================")
    print("     EXECUTING END-TO-END SEQUENTIAL MASTER INTEGRATION SCENARIO         ")
    print("==========================================================================")

    from fastapi.testclient import TestClient
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine, select, func

    TEST_DB_URL = "sqlite:///./test_master_scenario.db"
    if os.path.exists("./test_master_scenario.db"):
        try:
            os.remove("./test_master_scenario.db")
        except Exception:
            pass

    scenario_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=scenario_engine)
    ScenarioSession = sessionmaker(autocommit=False, autoflush=False, bind=scenario_engine)

    def override_scenario_db():
        db = ScenarioSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_scenario_db
    client = TestClient(app)

    db = ScenarioSession()

    # Seed Admin, Supervisor, Gate
    admin = User(email="master_admin@siteintel.com", password_hash=hash_password("AdminPass123!"), full_name="Master Admin", role=UserRole.ADMIN)
    supervisor = User(email="master_sup@siteintel.com", password_hash=hash_password("SupPass123!"), full_name="Master Supervisor", role=UserRole.SUPERVISOR)
    worker = User(email="master_worker@siteintel.com", password_hash=hash_password("WorkPass123!"), full_name="Master Worker", role=UserRole.WORKER)
    gate = Gate(name="Gate Master 1", location="East Perimeter")

    db.add_all([admin, supervisor, worker, gate])
    db.commit()
    db.refresh(admin)
    db.refresh(supervisor)
    db.refresh(worker)
    db.refresh(gate)

    admin_token = create_access_token(subject=admin.id, role=admin.role.value)
    supervisor_token = create_access_token(subject=supervisor.id, role=supervisor.role.value)

    # STEP 1: Log Violation via AI pipeline
    print("\n[Step 1] AI pipeline detects violation -> POST /api/v1/violations/internal...")
    viol_res = client.post(
        "/api/v1/violations/internal",
        headers={"Authorization": f"Bearer {supervisor_token}"},
        json={
            "gate_id": str(gate.id),
            "worker_id": str(worker.id),
            "violation_type": "ppe_missing",
            "helmet_missing": True,
            "vest_missing": False
        }
    )
    assert viol_res.status_code == 201
    viol_id = viol_res.json()["id"]
    print(f"  Logged Violation ID: {viol_id} | Initial Status: {viol_res.json()['status']}")
    assert viol_res.json()["status"] == "pending"

    # STEP 2: Acknowledge Violation via new endpoint
    print("\n[Step 2] Supervisor acknowledges violation -> PATCH /api/v1/violations/{id}/acknowledge...")
    ack_res = client.patch(
        f"/api/v1/violations/{viol_id}/acknowledge",
        headers={"Authorization": f"Bearer {supervisor_token}"},
        json={"notes": "Worker provided helmet on site."}
    )
    assert ack_res.status_code == 200
    print(f"  Updated Violation Status: {ack_res.json()['status']} | AckBy: {ack_res.json()['acknowledged_by']}")
    assert ack_res.json()["status"] == "acknowledged"

    # STEP 3: Initial Dashboard Summary
    print("\n[Step 3] Fetching Dashboard Summary -> GET /api/v1/dashboard/summary...")
    dash_1 = client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert dash_1.status_code == 200
    print(f"  Pending Escalations: {dash_1.json()['pending_escalations']} | System Health: {dash_1.json()['system_health']}")
    assert dash_1.json()["pending_escalations"] == 0

    # Seed AI vehicle count for gate
    ai_seed_log = DeliveryLog(gate_id=gate.id, reported_by=supervisor.id, ai_vehicle_count=2, manual_reported_count=2, material_type="cement", material_quantity=10.0, quantity_unit="bags", discrepancy_flag=False)
    db.add(ai_seed_log)
    db.commit()

    # STEP 4: Trigger Escalated Discrepancy (3 consecutive count mismatches)
    print("\n[Step 4] Logging 3 consecutive delivery count mismatches at Gate Master 1...")
    for i in range(3):
        d_res = client.post(
            "/api/v1/deliveries",
            headers={"Authorization": f"Bearer {supervisor_token}"},
            json={
                "gate_id": str(gate.id),
                "manual_reported_count": 5,
                "material_type": "sand",
                "material_quantity": 20.0,
                "quantity_unit": "tons"
            }
        )
        assert d_res.status_code == 201

    db_delivery = db.query(DeliveryLog).filter(DeliveryLog.discrepancy_flag == True).first()
    print(f"  Escalated Delivery Discrepancy ID: {db_delivery.id} | Resolved: {db_delivery.discrepancy_resolved}")

    # STEP 5: Dashboard Summary reflects pending_escalations = 1
    print("\n[Step 5] Fetching updated Dashboard Summary after escalation...")
    dash_2 = client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert dash_2.status_code == 200
    print(f"  Pending Escalations (Unresolved): {dash_2.json()['pending_escalations']}")
    assert dash_2.json()["pending_escalations"] >= 1

    # STEP 6: Admin Resolves Discrepancy via new endpoint
    print("\n[Step 6] Admin resolves delivery discrepancy -> PATCH /api/v1/deliveries/discrepancies/{id}/resolve...")
    res_res = client.patch(
        f"/api/v1/deliveries/discrepancies/{db_delivery.id}/resolve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "resolve", "notes": "Audited gate log; discrepancy resolved."}
    )
    assert res_res.status_code == 200
    print(f"  Discrepancy Resolved Flag: {res_res.json()['discrepancy_resolved']} | ResolvedBy: {res_res.json()['resolved_by']}")
    assert res_res.json()["discrepancy_resolved"] is True

    # STEP 7: Fresh Dashboard Summary -> pending_escalations count drops accordingly!
    print("\n[Step 7] Fetching fresh Dashboard Summary after resolution...")
    dash_3 = client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert dash_3.status_code == 200
    print(f"  Fresh Pending Escalations Count: {dash_3.json()['pending_escalations']}")
    
    # Direct DB query verification
    sql_unresolved = db.scalar(
        select(func.count()).select_from(DeliveryLog).where(
            DeliveryLog.discrepancy_flag == True,
            DeliveryLog.discrepancy_resolved == False
        )
    )
    print(f"  [Verification] Direct SQL Unresolved Discrepancies Count: {sql_unresolved}")
    print(f"  [Verification] Dashboard pending_escalations API: {dash_3.json()['pending_escalations']}")
    assert dash_3.json()["pending_escalations"] == sql_unresolved

    db.close()
    scenario_engine.dispose()
    app.dependency_overrides.clear()
    if os.path.exists("./test_master_scenario.db"):
        try:
            os.remove("./test_master_scenario.db")
        except Exception:
            pass

    print("\nSUCCESS: End-to-End Sequential Master Integration Scenario Verified!")

def run_master_retest_suite():
    print("\n==========================================================================")
    print("  SITE INTEL AI: MASTER RE-TEST SUITE (ALL PHASE TESTS & SPEC ADDITIONS)  ")
    print("==========================================================================")

    # 1. Auth & Password Security
    print("\n>>> EXECUTION BLOCK 1: AUTHENTICATION, JWT & SECURITY ROTATION")
    reset_test_db_override()
    test_password_hashing()
    test_jwt_token_generation_and_decoding()
    test_admin_vs_supervisor_authorization()
    test_refresh_token_rotation()
    test_login_rate_limiting()

    # 2. Phase 4 Core APIs & Discrepancy Logic
    print("\n>>> EXECUTION BLOCK 2: BACKEND CORE APIS & PYDANTIC STRICTNESS")
    reset_test_db_override()
    test_unit_discrepancy_service_consecutive_streak()
    test_extra_fields_pydantic_rejection()
    test_discrepancy_edge_case_no_ai_count()
    test_disallowed_file_upload_failure_case()
    test_integration_endpoints_and_auth_failures()

    # 3. Phase 4 Spec Alignment Additions
    print("\n>>> EXECUTION BLOCK 3: NEW SPEC-ALIGNMENT BACKEND API ENDPOINTS")
    test_acknowledge_violation_and_reacknowledge_409_conflict()

    # 4. Phase 6 AI Computer Vision Pipeline
    print("\n>>> EXECUTION BLOCK 4: AI COMPUTER VISION PIPELINE & DB INGESTION")
    reset_test_db_override()
    test_unit_confidence_threshold_logic()
    test_edge_case_empty_scene_zero_violations()
    test_failure_case_corrupted_unreadable_video()
    test_end_to_end_full_pipeline_demo()

    # 5. Real YOLOv8 Model Inference on All Pexels Demo Video Clips
    print("\n>>> EXECUTION BLOCK 5: REAL UN-MOCKED YOLOv8 MODEL ON PEXELS CLIPS")
    run_real_pexels_yolo_inference_benchmark()

    # 6. Phase 7 Advanced Features & Escalations
    print("\n>>> EXECUTION BLOCK 6: ADVANCED FEATURES & ADMIN ESCALATION NOTIFICATIONS")
    reset_test_db_override()
    test_integration_three_consecutive_mismatches_escalation()
    test_integration_single_mismatch_no_escalation()
    test_security_supervisor_forbidden_from_admin_escalation_endpoint()
    test_ai_hazard_categorization()

    # 7. End-to-End Sequential Master Integration Scenario
    print("\n>>> EXECUTION BLOCK 7: END-TO-END SEQUENTIAL MASTER SCENARIO")
    run_end_to_end_sequential_master_scenario()

    # 8. Phase 8 Security & Performance
    print("\n>>> EXECUTION BLOCK 8: SYSTEM SECURITY (JWT TAMPERING, SQLi) & PERFORMANCE")
    reset_test_db_override()
    test_security_jwt_tampering_rejection()
    test_security_sqli_parameterization()
    test_performance_concurrent_dashboard_requests()

    print("\n==========================================================================")
    print("  MASTER RE-TEST SUITE COMPLETED SUCCESSFULLY — ALL ENDPOINTS PASSED 100% ")
    print("==========================================================================")

def test_run_master_retest_suite():
    run_master_retest_suite()

if __name__ == "__main__":
    run_master_retest_suite()
