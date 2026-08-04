#!/bin/bash
set -e

echo "================================================================="
echo "   STARTING SITE INTEL AI BACKEND CONTAINER                      "
echo "================================================================="

echo ">>> Step 1: Running Alembic migrations to head..."
alembic upgrade head

echo ">>> Step 2: Running initial database seed..."
python -m app.db.seed

echo ">>> Step 3: Launching Uvicorn ASGI Web Server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
