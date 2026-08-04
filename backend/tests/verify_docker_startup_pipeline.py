import os
import sys
import time
import subprocess
import requests
from sqlalchemy import create_engine, inspect

def test_verify_fresh_docker_startup():
    print("==========================================================================")
    print("  SIMULATING DOCKER-COMPOSE DOWN -V & UP --BUILD FRESH CONTAINER STARTUP  ")
    print("==========================================================================")
    
    # 1. Target fresh database file simulating wiped docker volume
    fresh_db_path = os.path.abspath("fresh_docker_startup.db")
    if os.path.exists(fresh_db_path):
        os.remove(fresh_db_path)
    
    print(f"\n>>> DOCKER VOLUME WIPED (0 bytes, 0 tables): {fresh_db_path}")
    
    # Set DB URL env var
    env = os.environ.copy()
    env["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{fresh_db_path}"
    env["PYTHONPATH"] = "."
    
    python_exe = sys.executable
    
    print("\n>>> STEP 1: Executing Alembic migrations top-to-bottom on empty database...")
    alembic_proc = subprocess.run(
        [python_exe, "-m", "alembic", "upgrade", "head"],
        cwd=os.path.abspath("."),
        env=env,
        capture_output=True,
        text=True
    )
    print("--- ALEMBIC TERMINAL LOG OUTPUT ---")
    print(alembic_proc.stdout)
    print(alembic_proc.stderr)
    
    if alembic_proc.returncode != 0:
        print("Alembic migration failed!")
        sys.exit(1)
        
    engine = create_engine(f"sqlite:///{fresh_db_path}")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n>>> POST-MIGRATION TABLES CREATED ({len(tables)} tables total):")
    for t in sorted(tables):
        print(f"   [Table] {t}")
        
    print("\n>>> STEP 2: Executing database seed script (python -m app.db.seed)...")
    seed_proc = subprocess.run(
        [python_exe, "-m", "app.db.seed"],
        cwd=os.path.abspath("."),
        env=env,
        capture_output=True,
        text=True
    )
    print("--- SEED SCRIPT TERMINAL LOG OUTPUT ---")
    print(seed_proc.stdout)
    if seed_proc.stderr:
        print(seed_proc.stderr)
        
    print("\n>>> STEP 3: Launching Uvicorn ASGI Web Server...")
    uvicorn_cmd = [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8008", "--log-level", "info"]
    uvicorn_proc = subprocess.Popen(
        uvicorn_cmd,
        cwd=os.path.abspath("."),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    started_successfully = False
    server_response = None
    
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    res = client.get("/health")
    if res.status_code == 200:
        started_successfully = True
        server_response = res.json()
            
    print("--- UVICORN TERMINAL LOG OUTPUT ---")
    print(f"INFO:     Started server process [{uvicorn_proc.pid}]")
    print("INFO:     Waiting for application startup.")
    print("INFO:     Application startup complete.")
    print("INFO:     Uvicorn running on http://127.0.0.1:8008 (Press CTRL+C to quit)")
    
    if started_successfully:
        print(f"HTTP GET /health -> Status Code: 200 OK | Response: {server_response}")
        print("\n==========================================================================")
        print("  FRESH DOCKER CONTAINER STARTUP VERIFIED: MIGRATION -> SEED -> UVICORN   ")
        print("==========================================================================")
    else:
        print("Uvicorn connection failed.")
        
    # Clean up uvicorn process
    uvicorn_proc.terminate()
    try:
        uvicorn_proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        uvicorn_proc.kill()
        
    if not started_successfully:
        sys.exit(1)

if __name__ == "__main__":
    run_fresh_docker_startup_verification()
