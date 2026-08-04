import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.zone import Zone
from app.schemas.zone import ZoneCreateRequest, ZoneResponse

router = APIRouter()

@router.get("", response_model=List[ZoneResponse], summary="List Defined Polygon Zones (Admin & Supervisor)")
def list_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR]))
):
    """
    Retrieve list of defined polygon restricted zones.
    Restricted to Admin and Supervisor roles.
    """
    return db.query(Zone).order_by(Zone.created_at.desc()).all()

@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED, summary="Create Restricted Polygon Zone (Admin Only)")
def create_zone(
    zone_in: ZoneCreateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Define a new restricted polygon zone (Admin only).
    Validates that polygon_coords contains at least 3 unique non-degenerate points.
    Returns 400 Bad Request if polygon is degenerate or has fewer than 3 points.
    """
    zone = Zone(
        name=zone_in.name,
        zone_type=zone_in.zone_type,
        polygon_coords=zone_in.polygon_coords,
        camera_id=zone_in.camera_id,
        ppe_requirements=zone_in.ppe_requirements,
        is_active=zone_in.is_active,
        created_by=admin_user.id,
        created_at=datetime.utcnow()
    )

    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone
