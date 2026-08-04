import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserRole
from tests.test_db_config import TestingSessionLocal

client = TestClient(app)

def setup_test_users():
    db = TestingSessionLocal()
    db.query(User).delete()
    
    admin = User(
        id=uuid.uuid4(),
        email="admin_test@siteintel.com",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    supervisor = User(
        id=uuid.uuid4(),
        email="supervisor_test@siteintel.com",
        password_hash=hash_password("SuperPass123!"),
        full_name="Supervisor User",
        role=UserRole.SUPERVISOR
    )
    db.add_all([admin, supervisor])
    db.commit()
    db.refresh(admin)
    db.refresh(supervisor)
    db.close()
    return admin, supervisor

def test_admin_vs_supervisor_authorization():
    print("\n--- 1. TESTING ADMIN VS SUPERVISOR ROLE AUTHORIZATION ---")
    admin, supervisor = setup_test_users()

    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)
    supervisor_token = create_access_token(subject=str(supervisor.id), role=supervisor.role.value)

    # Test Admin Access on Admin-Only Route
    response_admin = client.get(
        "/api/v1/auth/test-protected",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"[Admin Token] GET /api/v1/auth/test-protected Status: {response_admin.status_code}")
    print(f"Response: {response_admin.json()}")
    assert response_admin.status_code == 200
    assert response_admin.json()["role"] == "admin"

    # Test Supervisor Access on Admin-Only Route
    response_supervisor = client.get(
        "/api/v1/auth/test-protected",
        headers={"Authorization": f"Bearer {supervisor_token}"}
    )
    print(f"[Supervisor Token] GET /api/v1/auth/test-protected Status: {response_supervisor.status_code}")
    print(f"Response: {response_supervisor.json()}")
    assert response_supervisor.status_code == 403
    assert "does not have sufficient permissions" in response_supervisor.json()["detail"]

def test_refresh_token_rotation():
    print("\n--- 2. TESTING STRICT REFRESH TOKEN ROTATION ---")
    admin, _ = setup_test_users()
    
    refresh_token_1 = create_refresh_token(subject=str(admin.id), role=admin.role.value)
    
    # First refresh: Should succeed and return NEW tokens
    resp1 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token_1})
    print(f"[First Refresh Attempt] Status: {resp1.status_code}")
    assert resp1.status_code == 200
    tokens_1 = resp1.json()
    refresh_token_2 = tokens_1["refresh_token"]
    assert refresh_token_2 != refresh_token_1

    # Second refresh with SAME OLD token (refresh_token_1): Should fail with 401 Unauthorized!
    resp2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token_1})
    print(f"[Reusing Revoked Refresh Token] Status: {resp2.status_code}")
    print(f"Response: {resp2.json()}")
    assert resp2.status_code == 401
    assert "already been used" in resp2.json()["detail"]

def test_login_rate_limiting():
    print("\n--- 3. TESTING LOGIN RATE LIMITING (THROTTLING ON 6TH ATTEMPT) ---")
    setup_test_users()

    statuses = []
    responses = []
    for i in range(1, 7):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@siteintel.com", "password": "wrongpassword"}
        )
        statuses.append(resp.status_code)
        responses.append(resp)
        print(f"Attempt #{i}: Status = {resp.status_code}")

    print(f"\nFinal 6th Attempt Response: {responses[-1].status_code} - {responses[-1].text}")
    assert statuses[-1] == 429

if __name__ == "__main__":
    test_admin_vs_supervisor_authorization()
    test_refresh_token_rotation()
    test_login_rate_limiting()
    print("\n=======================================================")
    print("ALL PHASE 3 SECURITY & AUTHORIZATION TESTS PASSED!")
    print("=======================================================")
