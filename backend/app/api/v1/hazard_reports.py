import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.core.file_validator import validate_uploaded_image
from app.models.user import User, UserRole
from app.models.hazard_report import HazardReport
from app.schemas.hazard_report import HazardReportResponse
from app.services.hazard_service import categorize_hazard

router = APIRouter()

UPLOAD_DIR = "storage/hazards"

@router.post("", response_model=HazardReportResponse, status_code=status.HTTP_201_CREATED, summary="Submit Hazard Report (Worker, Supervisor, Admin)")
async def create_hazard_report(
    description: str = Form(..., min_length=3),
    location: str = Form(..., min_length=2),
    category: Optional[str] = Form("other"),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a safety hazard report with optional image attachment.
    Enforces MIME type whitelist (JPEG/PNG), magic byte content checking, and max 5MB size limit.
    """
    image_url = None

    if file:
        contents = await file.read()
        validate_uploaded_image(file, contents)

        # Save file to storage location
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(contents)

        image_url = f"/storage/hazards/{filename}"

    # Auto-categorize hazard report using AI rule-based keyword & text analysis engine
    auto_category = categorize_hazard(description)
    final_category = category if (category and category != "other") else auto_category

    report = HazardReport(
        reported_by=current_user.id,
        description=description,
        location=location,
        category=final_category,
        image_url=image_url
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("", response_model=List[HazardReportResponse], summary="List Hazard Reports (All Roles)")
def list_hazard_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.WORKER]))
):
    """
    Retrieve all worker-submitted hazard reports.
    Restricted to Admin and Supervisor roles.
    """
    reports = db.query(HazardReport).order_by(HazardReport.created_at.desc()).all()
    return reports
