import io
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole
from app.models.gate import Gate
from app.models.zone import Zone
from app.models.violation import Violation
from app.models.hazard_report import HazardReport
from app.models.delivery_log import DeliveryLog
from app.models.equipment import Equipment
from app.services.discrepancy_service import evaluate_delivery_discrepancy
from tests.test_db_config import TestingSessionLocal

client = TestClient(app)

def setup_users_and_gate():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.query(Gate).delete()

    admin = User(
        id=uuid.uuid4(),
        email="admin_p4@siteintel.com",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin P4",
        role=UserRole.ADMIN
    )
    supervisor = User(
        id=uuid.uuid4(),
        email="supervisor_p4@siteintel.com",
        password_hash=hash_password("SuperPass123!"),
        full_name="Supervisor P4",
        role=UserRole.SUPERVISOR
    )
    worker = User(
        id=uuid.uuid4(),
        email="worker_p4@siteintel.com",
        password_hash=hash_password("WorkerPass123!"),
        full_name="Worker P4",
        role=UserRole.WORKER
    )

    gate = Gate(
        id=uuid.uuid4(),
        name="Gate Alpha",
        location="North Gate"
    )

    db.add_all([admin, supervisor, worker, gate])
    db.commit()
    db.refresh(admin)
    db.refresh(supervisor)
    db.refresh(worker)
    db.refresh(gate)
    db.close()
    return admin, supervisor, worker, gate

def test_unit_discrepancy_service_consecutive_streak():
    print("\n--- 1. UNIT TEST: CONSECUTIVE MISMATCH STREAK & RESET LOGIC ---")
    
    # (a) 2 consecutive mismatches at a gate does NOT escalate
    flag_2, esc_2 = evaluate_delivery_discrepancy(
        ai_vehicle_count=3,
        manual_reported_count=2,
        recent_gate_discrepancy_flags=[True]  # Only 1 prior mismatch
    )
    print(f"Test 1A (2 Total Mismatches: history=[True]) -> discrepancy_flag={flag_2}, is_escalated={esc_2}")
    assert flag_2 is True
    assert esc_2 is False

    # (b) Mismatch streak broken by a matching delivery resets counter
    flag_reset, esc_reset = evaluate_delivery_discrepancy(
        ai_vehicle_count=3,
        manual_reported_count=2,
        recent_gate_discrepancy_flags=[True, False]  # Previous was a MATCH (False), breaking the streak!
    )
    print(f"Test 1B (Broken Streak: history=[True, False]) -> discrepancy_flag={flag_reset}, is_escalated={esc_reset}")
    assert flag_reset is True
    assert esc_reset is False

    # (c) 3 consecutive mismatches triggers escalation
    flag_3, esc_3 = evaluate_delivery_discrepancy(
        ai_vehicle_count=3,
        manual_reported_count=2,
        recent_gate_discrepancy_flags=[True, True]  # 2 preceding mismatches -> this is the 3rd consecutive!
    )
    print(f"Test 1C (3rd Consecutive Mismatch: history=[True, True]) -> discrepancy_flag={flag_3}, is_escalated={esc_3}")
    assert flag_3 is True
    assert esc_3 is True

    print("SUCCESS: Confirmed 2 mismatches do not escalate AND broken streaks reset the counter!")

def test_extra_fields_pydantic_rejection():
    print("\n--- 2. PYDANTIC EXTRA FIELDS REJECTION TEST (extra='forbid') ---")
    _, supervisor, _, gate = setup_users_and_gate()
    supervisor_token = create_access_token(subject=supervisor.id, role=supervisor.role.value)

    # Request payload containing unauthorized/unexpected extra field ("is_admin": true)
    payload_with_extra_field = {
        "gate_id": str(gate.id),
        "manual_reported_count": 2,
        "material_type": "sand",
        "material_quantity": 10.5,
        "quantity_unit": "tons",
        "is_admin": True  # UNEXPECTED EXTRA FIELD
    }

    response = client.post(
        "/api/v1/deliveries",
        headers={"Authorization": f"Bearer {supervisor_token}"},
        json=payload_with_extra_field
    )

    print(f"[Extra Fields Rejection Test] Status Code: {response.status_code}")
    print(f"[Extra Fields Rejection Test] Response Body: {response.json()}")
    assert response.status_code == 422
    assert "extra_forbidden" in str(response.json()) or "Extra inputs are not permitted" in str(response.json())
    print("SUCCESS: Confirmed Pydantic schemas strictly reject requests containing unexpected extra fields!")

def test_discrepancy_edge_case_no_ai_count():
    print("\n--- 3. EDGE CASE TEST: DELIVERY LOG SUBMITTED BEFORE ANY AI COUNT EXISTS ---")
    flag, esc = evaluate_delivery_discrepancy(ai_vehicle_count=None, manual_reported_count=5)
    print(f"[Edge Case] Delivery submitted with AI count = None, Manual = 5 -> discrepancy_flag={flag}, is_escalated={esc}")
    assert flag is False
    assert esc is False
    print("SUCCESS: Confirmed delivery log submitted before AI count does NOT falsely flag as a discrepancy!")

def test_disallowed_file_upload_failure_case():
    print("\n--- 4. FAILURE CASE TEST: HAZARD REPORT WITH DISALLOWED FILE TYPE (.EXE / SCRIPT) ---")
    _, _, worker, _ = setup_users_and_gate()
    worker_token = create_access_token(subject=worker.id, role=worker.role.value)

    fake_exe_content = b"MZ\x90\x00\x03\x00\x00\x00THIS IS AN EXECUTABLE SCRIPT"
    disallowed_file = ("malicious.exe", io.BytesIO(fake_exe_content), "application/x-msdownload")

    response = client.post(
        "/api/v1/hazard-reports",
        headers={"Authorization": f"Bearer {worker_token}"},
        data={"description": "Exposed high voltage cable near scaffold", "location": "Zone A Sector 2", "category": "unsafe_wiring"},
        files={"file": disallowed_file}
    )

    print(f"[Upload Failure Test] Status Code: {response.status_code}")
    print(f"[Upload Failure Test] Response Body: {response.json()}")
    assert response.status_code == 400
    assert "Disallowed file MIME type" in response.json()["detail"] or "does not match a valid JPEG or PNG" in response.json()["detail"]
    print("SUCCESS: Confirmed disallowed file upload rejected with HTTP 400 Bad Request!")

def test_integration_endpoints_and_auth_failures():
    print("\n--- 5. INTEGRATION TESTS: AUTH FAILURES (401 NO TOKEN, 403 WRONG ROLE) & ENDPOINTS ---")
    admin, supervisor, _, _ = setup_users_and_gate()

    admin_token = create_access_token(subject=admin.id, role=admin.role.value)
    supervisor_token = create_access_token(subject=supervisor.id, role=supervisor.role.value)

    # Test 1: No Token -> 401 Unauthorized
    resp_no_token = client.get("/api/v1/violations")
    print(f"[No Token Test] GET /api/v1/violations -> Status: {resp_no_token.status_code}")
    assert resp_no_token.status_code == 401

    # Test 2: Supervisor accessing Admin-Only Discrepancies Endpoint -> 403 Forbidden
    resp_forbidden = client.get(
        "/api/v1/deliveries/discrepancies",
        headers={"Authorization": f"Bearer {supervisor_token}"}
    )
    print(f"[Supervisor Access Admin Route] GET /api/v1/deliveries/discrepancies -> Status: {resp_forbidden.status_code}")
    assert resp_forbidden.status_code == 403

    # Test 3: Admin Access Admin-Only Discrepancies Endpoint -> 200 OK
    resp_admin_disc = client.get(
        "/api/v1/deliveries/discrepancies",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"[Admin Access Admin Route] GET /api/v1/deliveries/discrepancies -> Status: {resp_admin_disc.status_code}")
    assert resp_admin_disc.status_code == 200

if __name__ == "__main__":
    test_unit_discrepancy_service_consecutive_streak()
    test_extra_fields_pydantic_rejection()
    test_discrepancy_edge_case_no_ai_count()
    test_disallowed_file_upload_failure_case()
    test_integration_endpoints_and_auth_failures()
    print("\n=======================================================")
    print("ALL PHASE 4 GAPS & SECURITY TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")
