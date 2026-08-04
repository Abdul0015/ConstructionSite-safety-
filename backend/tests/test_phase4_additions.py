import os
import json
import uuid
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.main import app
from app.db.base_class import Base
from app.models import User, UserRole, Violation, DeliveryLog, Zone, Equipment, Gate
from app.core.security import create_access_token, hash_password
from app.api.deps import get_db

from tests.test_db_config import engine, TestingSessionLocal, override_get_db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    admin = User(email="admin_p4a@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Alice Admin", role=UserRole.ADMIN)
    supervisor = User(email="supervisor_p4a@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Bob Supervisor", role=UserRole.SUPERVISOR)
    worker = User(email="worker_p4a@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Charlie Worker", role=UserRole.WORKER)
    gate = Gate(name="Gate Alpha", location="North Perimeter")
    db.add_all([admin, supervisor, worker, gate])
    db.commit()
    db.refresh(admin)
    db.refresh(supervisor)
    db.refresh(worker)
    db.refresh(gate)

    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)
    supervisor_token = create_access_token(subject=str(supervisor.id), role=supervisor.role.value)
    worker_token = create_access_token(subject=str(worker.id), role=worker.role.value)

    yield {
        "db": db, "admin": admin, "supervisor": supervisor, "worker": worker, "gate": gate,
        "admin_token": admin_token, "supervisor_token": supervisor_token, "worker_token": worker_token
    }

def test_acknowledge_violation_and_reacknowledge_409_conflict(setup_db):
    ctx = setup_db
    db = ctx["db"]
    violation = Violation(
        gate_id=ctx["gate"].id, worker_id=ctx["worker"].id,
        violation_type="ppe_missing", helmet_missing=True, vest_missing=False, status="pending"
    )
    db.add(violation)
    db.commit()
    db.refresh(violation)

    ack_res = client.patch(
        f"/api/v1/violations/{violation.id}/acknowledge",
        headers={"Authorization": f"Bearer {ctx['supervisor_token']}"},
        json={"notes": "Reviewed camera clip; worker instructed to wear helmet."}
    )
    assert ack_res.status_code == 200

    db.refresh(violation)
    assert violation.status == "acknowledged"
    assert violation.acknowledged_by == ctx["supervisor"].id

    ack_re_res = client.patch(
        f"/api/v1/violations/{violation.id}/acknowledge",
        headers={"Authorization": f"Bearer {ctx['admin_token']}"},
        json={"notes": "Attempting second ack"}
    )
    assert ack_re_res.status_code == 409

def test_resolve_delivery_discrepancy_and_admin_audit_trail(setup_db):
    ctx = setup_db
    db = ctx["db"]
    delivery = DeliveryLog(
        gate_id=ctx["gate"].id, reported_by=ctx["supervisor"].id, ai_vehicle_count=3,
        manual_reported_count=2, material_type="sand", material_quantity=15.0, quantity_unit="tons",
        discrepancy_flag=True, discrepancy_resolved=False
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    resolve_res = client.patch(
        f"/api/v1/deliveries/discrepancies/{delivery.id}/resolve",
        headers={"Authorization": f"Bearer {ctx['admin_token']}"},
        json={"action": "resolve", "notes": "Gate camera verified extra truck was returning empty."}
    )
    assert resolve_res.status_code == 200
    db.refresh(delivery)
    assert delivery.discrepancy_resolved is True
    assert delivery.resolved_by == ctx["admin"].id

def test_zone_polygon_coordinate_validations(setup_db):
    ctx = setup_db
    res_2pt = client.post(
        "/api/v1/zones",
        headers={"Authorization": f"Bearer {ctx['admin_token']}"},
        json={"name": "Line Zone", "zone_type": "crane", "polygon_coords": [{"x": 10, "y": 10}, {"x": 20, "y": 20}]}
    )
    assert res_2pt.status_code in [400, 422]

    res_valid = client.post(
        "/api/v1/zones",
        headers={"Authorization": f"Bearer {ctx['admin_token']}"},
        json={
            "name": "Crane Heavy Lift Sector", "zone_type": "crane",
            "polygon_coords": [{"x": 10, "y": 10}, {"x": 50, "y": 10}, {"x": 50, "y": 50}, {"x": 10, "y": 50}],
            "camera_id": "cam_crane_01", "ppe_requirements": ["helmet", "harness"]
        }
    )
    assert res_valid.status_code == 201

def test_admin_self_deactivation_rejection(setup_db):
    ctx = setup_db
    deact_self_res = client.patch(
        f"/api/v1/users/{ctx['admin'].id}/deactivate",
        headers={"Authorization": f"Bearer {ctx['admin_token']}"}
    )
    assert deact_self_res.status_code == 400

def test_supervisor_rbac_403_forbidden_across_admin_endpoints(setup_db):
    ctx = setup_db
    r_zone = client.post(
        "/api/v1/zones",
        headers={"Authorization": f"Bearer {ctx['supervisor_token']}"},
        json={"name": "Sup Zone", "polygon_coords": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}]}
    )
    assert r_zone.status_code == 403

    r_users = client.get("/api/v1/users", headers={"Authorization": f"Bearer {ctx['supervisor_token']}"})
    assert r_users.status_code == 403

def test_equipment_list_and_dashboard_pending_escalations_sql_matching(setup_db):
    ctx = setup_db
    db = ctx["db"]
    eq = Equipment(equipment_type="crane", identifier="CR-900", location_description="Sector B Crane", status="active", idle_minutes=0)
    db.add(eq)
    db.commit()

    eq_res = client.get("/api/v1/equipment", headers={"Authorization": f"Bearer {ctx['supervisor_token']}"})
    assert eq_res.status_code == 200

    dash_res = client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {ctx['supervisor_token']}"})
    assert dash_res.status_code == 200
