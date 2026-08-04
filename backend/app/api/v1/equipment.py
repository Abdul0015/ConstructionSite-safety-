import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentResponse

router = APIRouter()

@router.get("", response_model=List[EquipmentResponse], summary="List Heavy Equipment Status (Admin & Supervisor)")
def list_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR]))
):
    """
    Retrieve heavy machinery equipment tracking log (excavator, bulldozer, crane, truck).
    Reads directly from the real 'equipment' database table.
    Note: If no active AI detection worker pipeline is feeding live updates to this table,
    results reflect database records directly.
    """
    return db.query(Equipment).order_by(Equipment.created_at.desc()).all()
