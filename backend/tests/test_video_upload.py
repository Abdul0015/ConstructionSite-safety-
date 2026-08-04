import json
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

def test_video_upload_endpoint():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    admin = User(email="admin_vup@siteintel.com", password_hash=hash_password("Pass123!"), full_name="Admin Vup", role=UserRole.ADMIN)
    gate = Gate(name="Gate Vup", location="Main Entrance")
    db.add_all([admin, gate])
    db.commit()

    token = create_access_token(subject=str(admin.id), role=admin.role.value)
    
    with open('storage/demo_clips/demo_compliant.mp4', 'rb') as f:
        file_bytes = f.read()

    res = client.post(
        '/api/v1/violations/process-video',
        headers={'Authorization': f'Bearer {token}'},
        files={'file': ('demo_compliant.mp4', file_bytes, 'video/mp4')}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "violations_detected" in data
