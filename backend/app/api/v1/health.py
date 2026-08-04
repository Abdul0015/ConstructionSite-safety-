from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health Check Endpoint")
def health_check():
    return {
        "status": "ok",
        "service": "site-intelligence-backend",
        "version": "1.0.0"
    }
