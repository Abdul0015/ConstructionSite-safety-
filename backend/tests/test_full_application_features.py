import json
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_db
from app.db.base_class import Base
from app.models import User, UserRole, Gate
from app.core.security import create_access_token, hash_password
from tests.test_db_config import engine, TestingSessionLocal, override_get_db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_app_features_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    admin = User(email="admin_faf@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Admin Faf", role=UserRole.ADMIN)
    supervisor = User(email="sup_faf@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Sup Faf", role=UserRole.SUPERVISOR)
    worker = User(email="worker_faf@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Worker Faf", role=UserRole.WORKER)
    gate = Gate(name="Gate Faf", location="Main Site")
    db.add_all([admin, supervisor, worker, gate])
    db.commit()

    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)
    supervisor_token = create_access_token(subject=str(supervisor.id), role=supervisor.role.value)
    worker_token = create_access_token(subject=str(worker.id), role=worker.role.value)

    yield {
        "db": db, "admin": admin, "supervisor": supervisor, "worker": worker, "gate": gate,
        "admin_token": admin_token, "supervisor_token": supervisor_token, "worker_token": worker_token
    }

def test_auth_credentials_generation(setup_app_features_db):
    ctx = setup_app_features_db
    assert ctx["admin_token"] is not None
    assert ctx["supervisor_token"] is not None
    assert ctx["worker_token"] is not None

def test_get_current_user_profile(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200
    assert res.json()["email"] == ctx["admin"].email

def test_get_dashboard_summary_kpis(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200
    assert "worker_count" in res.json()

def test_get_violations_and_acknowledge_action(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/violations", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200

def test_get_user_management_list(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/users", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200
    assert len(res.json()) >= 3

def test_submit_delivery_log_form(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.post(
        "/api/v1/deliveries",
        json={
            "gate_id": str(ctx["gate"].id),
            "manual_reported_count": 5,
            "material_type": "steel",
            "material_quantity": 25.5,
            "quantity_unit": "tons",
            "vehicle_type": "flatbed_truck"
        },
        headers={"Authorization": f"Bearer {ctx['supervisor_token']}"}
    )
    assert res.status_code == 201

def test_get_material_inflow_summary(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/deliveries/materials", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200

def test_get_zones_list(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/zones", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200

def test_get_equipment_list(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.get("/api/v1/equipment", headers={"Authorization": f"Bearer {ctx['admin_token']}"})
    assert res.status_code == 200

def test_submit_hazard_report_form(setup_app_features_db):
    ctx = setup_app_features_db
    res = client.post(
        "/api/v1/hazard-reports",
        data={
            "description": "Exposed high-voltage conduit near West Scaffold",
            "location": "Sector 4 Scaffold",
            "category": "unsafe_wiring"
        },
        headers={"Authorization": f"Bearer {ctx['worker_token']}"}
    )
    assert res.status_code == 201
