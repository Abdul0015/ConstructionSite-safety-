import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_db
from app.db.base_class import Base
from app.models import User, UserRole
from app.core.security import create_access_token, hash_password
from tests.test_db_config import engine, TestingSessionLocal, override_get_db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_zone_validation_payloads():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    admin = User(email="admin_zoneval@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Admin ZoneVal", role=UserRole.ADMIN)
    db.add(admin)
    db.commit()

    token = create_access_token(subject=str(admin.id), role=admin.role.value)

    # Request 1: Degenerate polygon (2 points)
    payload1 = {
        'name': 'Bad Zone',
        'zone_type': 'excavation',
        'polygon_coords': [{'x': 1, 'y': 1}, {'x': 2, 'y': 2}],
        'site_location': 'North'
    }
    res1 = client.post(
        '/api/v1/zones',
        json=payload1,
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res1.status_code == 422

    # Request 2: Genuinely malformed JSON syntax / invalid datatype
    res2 = client.post(
        '/api/v1/zones',
        content=b'{"name": "Malformed Zone", "polygon_coords": [{"x": 1, "y": 2}',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    )
    assert res2.status_code == 422
