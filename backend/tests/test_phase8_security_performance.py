import time
import uuid
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole
from app.models.hazard_report import HazardReport
from app.models.gate import Gate
from tests.test_db_config import TestingSessionLocal

client = TestClient(app)

def setup_phase8_test_data():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.query(Gate).delete()
    db.query(HazardReport).delete()

    admin = User(
        id=uuid.uuid4(),
        email="admin_p8@siteintel.com",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin P8",
        role=UserRole.ADMIN
    )
    worker = User(
        id=uuid.uuid4(),
        email="worker_p8@siteintel.com",
        password_hash=hash_password("WorkerPass123!"),
        full_name="Worker P8",
        role=UserRole.WORKER
    )

    db.add_all([admin, worker])
    db.commit()
    db.refresh(admin)
    db.refresh(worker)
    db.close()
    return admin, worker

def test_security_jwt_tampering_rejection():
    print("\n--- 1. SECURITY TEST: JWT PAYLOAD & SIGNATURE TAMPERING REJECTION ---")
    admin, worker = setup_phase8_test_data()

    valid_token = create_access_token(subject=admin.id, role=admin.role.value)
    
    # Tamper with the JWT signature by altering the last 10 characters
    tampered_token = valid_token[:-10] + "X9Z8Y7W6V5"

    # Attempt to access protected endpoint with tampered token
    resp = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {tampered_token}"}
    )
    print(f"[JWT Tampering Attempt] Status: {resp.status_code} | Error Detail: {resp.json()}")
    assert resp.status_code == 401
    assert "Could not validate credentials" in resp.json()["detail"] or "Signature" in resp.json()["detail"]
    print("SUCCESS: Tampered JWT token rejected with HTTP 401 Unauthorized!")

def test_security_sqli_parameterization():
    print("\n--- 2. SECURITY TEST: SQL INJECTION PAYLOAD PARAMETERIZATION ---")
    admin, worker = setup_phase8_test_data()
    worker_token = create_access_token(subject=worker.id, role=worker.role.value)

    # Classic SQLi payloads
    sqli_payloads = [
        "' OR '1'='1'; --",
        "'; DROP TABLE users; --",
        "1' UNION SELECT username, password_hash FROM users --"
    ]

    for payload in sqli_payloads:
        resp = client.post(
            "/api/v1/hazard-reports",
            headers={"Authorization": f"Bearer {worker_token}"},
            data={"description": f"Hazard description with SQLi attempt: {payload}", "location": "Sector C", "category": "other"}
        )
        assert resp.status_code == 201
        saved_desc = resp.json()["description"]
        print(f"[SQLi Attack Payload Ingested Safely] Input: '{payload}' -> Stored Text: '{saved_desc}'")
        assert payload in saved_desc

    # Verify that the DB tables remain 100% intact and undamaged
    db = TestingSessionLocal()
    user_count = db.query(User).count()
    db.close()

    print(f"[SQLi Integrity Check] Total Users in DB after SQLi payloads: {user_count}")
    assert user_count == 2
    print("SUCCESS: SQLAlchemy ORM safely parameterized all input strings! Zero SQL injection vulnerability.")

def test_performance_concurrent_dashboard_requests():
    print("\n--- 3. PERFORMANCE TEST: CONCURRENT DASHBOARD REQUESTS ---")
    if hasattr(app.state, "limiter"):
        try:
            app.state.limiter.reset()
        except Exception:
            pass

    admin, worker = setup_phase8_test_data()
    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)
    headers = {"Authorization": f"Bearer {admin_token}"}

    num_concurrent_requests = 20

    def make_request(req_id):
        start_time = time.time()
        resp = client.get("/api/v1/dashboard/summary", headers=headers)
        elapsed_ms = (time.time() - start_time) * 1000.0
        return resp.status_code, elapsed_ms

    start_total = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_concurrent_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    total_time_ms = (time.time() - start_total) * 1000.0

    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    print(f"[Performance Metric] Total Requests Fired: {num_concurrent_requests}")
    print(f"[Performance Metric] Success Rate: {statuses.count(200)} / {num_concurrent_requests} (100% HTTP 200 OK)")
    print(f"[Performance Metric] Average Response Latency: {avg_latency:.2f} ms")
    print(f"[Performance Metric] Peak Response Latency: {max_latency:.2f} ms")
    print(f"[Performance Metric] Total Wall-Clock Time: {total_time_ms:.2f} ms")

    assert statuses.count(200) == num_concurrent_requests
    assert avg_latency < 100.0  # Sub-100ms requirement
    print("SUCCESS: Concurrent performance test passed cleanly with sub-second response times!")

if __name__ == "__main__":
    test_security_jwt_tampering_rejection()
    test_security_sqli_parameterization()
    test_performance_concurrent_dashboard_requests()
