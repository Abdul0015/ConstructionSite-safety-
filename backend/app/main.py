from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.violations import router as violations_router
from app.api.v1.hazard_reports import router as hazard_reports_router
from app.api.v1.deliveries import router as deliveries_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.zones import router as zones_router
from app.api.v1.users import router as users_router
from app.api.v1.equipment import router as equipment_router

from app.db.base_class import Base
from app.db.session import engine
from app.db.seed import seed_db

Base.metadata.create_all(bind=engine)
try:
    seed_db()
except Exception:
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG
)

# Register rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for restricted frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("storage", exist_ok=True)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include versioned API routes
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication & Authorization"])
app.include_router(violations_router, prefix=f"{settings.API_V1_STR}/violations", tags=["PPE & Zone Violations"])
app.include_router(hazard_reports_router, prefix=f"{settings.API_V1_STR}/hazard-reports", tags=["Hazard Reports"])
app.include_router(deliveries_router, prefix=f"{settings.API_V1_STR}/deliveries", tags=["Delivery & Material Logging"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Central Dashboard"])
app.include_router(zones_router, prefix=f"{settings.API_V1_STR}/zones", tags=["Restricted Zone Management"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["User Account Management"])
app.include_router(equipment_router, prefix=f"{settings.API_V1_STR}/equipment", tags=["Equipment Tracking"])

@app.get("/health", tags=["Health"])
def root_health():
    return {"status": "ok", "service": "site-intelligence-backend"}
