import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole
from app.models.gate import Gate
from app.models.delivery_log import DeliveryLog
from app.models.admin_notification import AdminNotification
from app.models.hazard_report import HazardReport
from app.services.hazard_service import categorize_hazard
from tests.test_db_config import TestingSessionLocal

client = TestClient(app)

def setup_phase7_test_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.query(Gate).delete()
    db.query(DeliveryLog).delete()
    db.query(AdminNotification).delete()
    db.query(HazardReport).delete()

    admin = User(
        id=uuid.uuid4(),
        email="admin_p7@siteintel.com",
        password_hash=hash_password("AdminPass123!"),
        full_name="Site Admin",
        role=UserRole.ADMIN
    )
    supervisor = User(
        id=uuid.uuid4(),
        email="supervisor_p7@siteintel.com",
        password_hash=hash_password("SuperPass123!"),
        full_name="Site Supervisor",
        role=UserRole.SUPERVISOR
    )
    worker = User(
        id=uuid.uuid4(),
        email="worker_p7@siteintel.com",
        password_hash=hash_password("WorkerPass123!"),
        full_name="Site Worker",
        role=UserRole.WORKER
    )
    gate = Gate(
        id=uuid.uuid4(),
        name="Gate Alpha",
        location="North Entry"
    )

    db.add_all([admin, supervisor, worker, gate])
    db.commit()
    db.refresh(admin)
    db.refresh(supervisor)
    db.refresh(worker)
    db.refresh(gate)
    db.close()
    return admin, supervisor, worker, gate

def test_integration_three_consecutive_mismatches_escalation():
    print("\n--- 1. INTEGRATION TEST: 3 CONSECUTIVE MISMATCHES -> ESCALATION & NOTIFICATION CREATED ---")
    admin, supervisor, worker, gate = setup_phase7_test_data()
    supervisor_token = create_access_token(subject=supervisor.id, role=supervisor.role.value)
    headers = {"Authorization": f"Bearer {supervisor_token}"}

    # Seed an AI vehicle count log at this gate (ai_vehicle_count = 2)
    db = TestingSessionLocal()
    seed_log = DeliveryLog(
        gate_id=gate.id,
        reported_by=supervisor.id,
        ai_vehicle_count=2,
        manual_reported_count=2,
        material_type="steel",
        material_quantity=10.0,
        quantity_unit="tons",
        discrepancy_flag=False
    )
    db.add(seed_log)
    db.commit()
    db.close()

    # Mismatch 1: manual = 5 (AI = 2) -> discrepancy_flag = True, notifications = 0
    resp1 = client.post("/api/v1/deliveries", headers=headers, json={
        "gate_id": str(gate.id), "manual_reported_count": 5,
        "material_type": "steel", "material_quantity": 10.0, "quantity_unit": "tons"
    })
    assert resp1.status_code == 201
    assert resp1.json()["discrepancy_flag"] is True

    db = TestingSessionLocal()
    notifs1 = db.query(AdminNotification).count()
    db.close()
    print(f"[Mismatch 1/3 Logged] Discrepancy Flag: True | Admin Notifications Created: {notifs1}")
    assert notifs1 == 0

    # Mismatch 2: manual = 5 (AI = 2) -> discrepancy_flag = True, notifications = 0
    resp2 = client.post("/api/v1/deliveries", headers=headers, json={
        "gate_id": str(gate.id), "manual_reported_count": 5,
        "material_type": "steel", "material_quantity": 10.0, "quantity_unit": "tons"
    })
    assert resp2.status_code == 201
    assert resp2.json()["discrepancy_flag"] is True

    db = TestingSessionLocal()
    notifs2 = db.query(AdminNotification).count()
    db.close()
    print(f"[Mismatch 2/3 Logged] Discrepancy Flag: True | Admin Notifications Created: {notifs2}")
    assert notifs2 == 0

    # Mismatch 3 (3rd CONSECUTIVE): manual = 5 (AI = 2) -> discrepancy_flag = True -> ESCALATED -> Notification Created!
    resp3 = client.post("/api/v1/deliveries", headers=headers, json={
        "gate_id": str(gate.id), "manual_reported_count": 5,
        "material_type": "steel", "material_quantity": 10.0, "quantity_unit": "tons"
    })
    assert resp3.status_code == 201
    assert resp3.json()["discrepancy_flag"] is True

    db = TestingSessionLocal()
    notifs3 = db.query(AdminNotification).all()
    db.close()
    print(f"[Mismatch 3/3 Logged - CONSECUTIVE STREAK 3] Discrepancy Flag: True | Admin Notifications Created: {len(notifs3)}")
    assert len(notifs3) == 1
    
    notif = notifs3[0]
    print(f"  -> DB Notification Row ID: {notif.id}")
    print(f"  -> Title: {notif.title}")
    print(f"  -> Message: {notif.message}")
    print(f"  -> Severity: {notif.severity}")
    assert notif.severity == "critical"
    print("SUCCESS: 3 consecutive mismatches triggered real escalation and logged AdminNotification DB record!")

def test_integration_single_mismatch_no_escalation():
    print("\n--- 2. INTEGRATION TEST: SINGLE MISMATCH -> NO ESCALATION, NO NOTIFICATION ---")
    admin, supervisor, worker, gate = setup_phase7_test_data()
    supervisor_token = create_access_token(subject=supervisor.id, role=supervisor.role.value)
    headers = {"Authorization": f"Bearer {supervisor_token}"}

    # Seed AI count = 1
    db = TestingSessionLocal()
    seed_log = DeliveryLog(
        gate_id=gate.id, reported_by=supervisor.id, ai_vehicle_count=1, manual_reported_count=1,
        material_type="cement", material_quantity=5.0, quantity_unit="bags", discrepancy_flag=False
    )
    db.add(seed_log)
    db.commit()
    db.close()

    # Single Mismatch: manual = 3 (AI = 1)
    resp = client.post("/api/v1/deliveries", headers=headers, json={
        "gate_id": str(gate.id), "manual_reported_count": 3,
        "material_type": "cement", "material_quantity": 5.0, "quantity_unit": "bags"
    })
    assert resp.status_code == 201
    assert resp.json()["discrepancy_flag"] is True

    db = TestingSessionLocal()
    notifs = db.query(AdminNotification).count()
    db.close()

    print(f"[Single Mismatch Result] Discrepancy Flag: True | Admin Notifications Created: {notifs}")
    assert notifs == 0
    print("SUCCESS: Single mismatch flagged record cleanly without falsely triggering escalation notification!")

def test_security_supervisor_forbidden_from_admin_escalation_endpoint():
    print("\n--- 3. SECURITY TEST: SUPERVISOR FORBIDDEN FROM ADMIN ESCALATIONS ENDPOINT ---")
    admin, supervisor, worker, gate = setup_phase7_test_data()

    supervisor_token = create_access_token(subject=supervisor.id, role=supervisor.role.value)
    admin_token = create_access_token(subject=admin.id, role=admin.role.value)

    # 1. Supervisor attempts direct API call to GET /api/v1/deliveries/escalations -> Must be HTTP 403 Forbidden!
    sup_resp = client.get(
        "/api/v1/deliveries/escalations",
        headers={"Authorization": f"Bearer {supervisor_token}"}
    )
    print(f"[Supervisor Direct Access Attempt] HTTP Status Code: {sup_resp.status_code} | Detail: {sup_resp.json()}")
    assert sup_resp.status_code == 403
    assert "does not have sufficient permissions" in sup_resp.json()["detail"]

    # 2. Admin attempts direct API call to GET /api/v1/deliveries/escalations -> Allowed (HTTP 200 OK)
    admin_resp = client.get(
        "/api/v1/deliveries/escalations",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"[Admin Access Attempt] HTTP Status Code: {admin_resp.status_code} | Total Escalations Returned: {len(admin_resp.json())}")
    assert admin_resp.status_code == 200
    print("SUCCESS: Security control verified! Supervisor blocked (403), Admin allowed (200).")

def test_ai_hazard_categorization():
    print("\n--- 4. AI HAZARD CATEGORIZATION TEST ---")
    admin, supervisor, worker, gate = setup_phase7_test_data()
    worker_token = create_access_token(subject=worker.id, role=worker.role.value)

    # Electrical hazard
    resp_elec = client.post(
        "/api/v1/hazard-reports",
        headers={"Authorization": f"Bearer {worker_token}"},
        data={"description": "Exposed electrical wires sparking near puddle", "location": "Sector A", "category": "other"}
    )
    assert resp_elec.status_code == 201
    print(f"[Hazard Report 1] Description: '{resp_elec.json()['description']}' -> Auto Category: '{resp_elec.json()['category']}'")
    assert resp_elec.json()["category"] == "electrical"

    # Structural hazard
    resp_struct = client.post(
        "/api/v1/hazard-reports",
        headers={"Authorization": f"Bearer {worker_token}"},
        data={"description": "Cracked scaffold beam near Sector 4", "location": "Sector B", "category": "other"}
    )
    assert resp_struct.status_code == 201
    print(f"[Hazard Report 2] Description: '{resp_struct.json()['description']}' -> Auto Category: '{resp_struct.json()['category']}'")
    assert resp_struct.json()["category"] == "structural"

    print("SUCCESS: Rule-based AI hazard categorization verified!")

if __name__ == "__main__":
    test_integration_three_consecutive_mismatches_escalation()
    test_integration_single_mismatch_no_escalation()
    test_security_supervisor_forbidden_from_admin_escalation_endpoint()
    test_ai_hazard_categorization()
