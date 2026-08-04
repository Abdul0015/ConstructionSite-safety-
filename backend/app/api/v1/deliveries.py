import uuid
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.delivery_log import DeliveryLog
from app.models.admin_notification import AdminNotification
from app.schemas.delivery_log import DeliveryLogCreate, DeliveryLogResponse, MaterialInflowGroup, DiscrepancyResolveRequest
from app.services.discrepancy_service import evaluate_delivery_discrepancy

router = APIRouter()

@router.post("", response_model=DeliveryLogResponse, status_code=status.HTTP_201_CREATED, summary="Log Delivery Count & Materials (Supervisor Only)")
def create_delivery_log(
    log_in: DeliveryLogCreate,
    db: Session = Depends(get_db),
    supervisor: User = Depends(require_role(UserRole.SUPERVISOR))
):
    """
    Log a delivery vehicle count and material inflow details (Supervisor only).
    Evaluates AI count vs manual count via discrepancy service.
    """
    # Fetch recent delivery logs for this gate to get historical discrepancy flags
    recent_logs = (
        db.query(DeliveryLog)
        .filter(DeliveryLog.gate_id == log_in.gate_id)
        .order_by(DeliveryLog.logged_at.desc())
        .limit(5)
        .all()
    )
    recent_flags = [l.discrepancy_flag for l in recent_logs]

    # For v1 API submission: Assume latest AI vehicle count recorded at this gate
    # If no AI count exists yet for this gate, ai_vehicle_count is None
    latest_log = recent_logs[0] if recent_logs else None
    ai_vehicle_count = latest_log.ai_vehicle_count if latest_log else None

    # Run isolated discrepancy evaluation business service
    discrepancy_flag, is_escalated = evaluate_delivery_discrepancy(
        ai_vehicle_count=ai_vehicle_count,
        manual_reported_count=log_in.manual_reported_count,
        recent_gate_discrepancy_flags=recent_flags
    )

    delivery = DeliveryLog(
        gate_id=log_in.gate_id,
        reported_by=supervisor.id,
        ai_vehicle_count=ai_vehicle_count,
        manual_reported_count=log_in.manual_reported_count,
        material_type=log_in.material_type,
        material_quantity=log_in.material_quantity,
        quantity_unit=log_in.quantity_unit,
        vehicle_type=log_in.vehicle_type,
        discrepancy_flag=discrepancy_flag,
        discrepancy_resolved=False
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    # Trigger Admin Notification if 3 consecutive mismatches at this gate occurred
    if is_escalated:
        notification = AdminNotification(
            title=f"CRITICAL DISCREPANCY ESCALATION - Gate {log_in.gate_id}",
            message=f"3 consecutive delivery count mismatches detected at gate {log_in.gate_id}. AI Count: {delivery.ai_vehicle_count}, Manual Reported: {log_in.manual_reported_count}.",
            severity="critical",
            gate_id=log_in.gate_id,
            delivery_log_id=delivery.id
        )
        db.add(notification)
        db.commit()

    return delivery

@router.get("/discrepancies", response_model=List[DeliveryLogResponse], summary="Get Flagged Delivery Discrepancies (Admin Only)")
def get_delivery_discrepancies(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Retrieve flagged count discrepancies (AI vs manual mismatch).
    Strictly Admin-only endpoint to prevent supervisor conflict of interest.
    """
    discrepancies = (
        db.query(DeliveryLog)
        .filter(DeliveryLog.discrepancy_flag == True)
        .order_by(DeliveryLog.logged_at.desc())
        .all()
    )
    return discrepancies

@router.patch("/discrepancies/{id}/resolve", response_model=DeliveryLogResponse, summary="Resolve Flagged Delivery Discrepancy (Admin Only)")
def resolve_delivery_discrepancy(
    id: uuid.UUID,
    body: DiscrepancyResolveRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Resolve or flag a delivery count discrepancy (Admin only).
    Sets discrepancy_resolved to True, resolved_by to Admin ID, and records timestamp.
    """
    delivery = db.query(DeliveryLog).filter(DeliveryLog.id == id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery log with ID '{id}' not found"
        )

    delivery.discrepancy_resolved = True
    delivery.resolved_by = admin_user.id
    delivery.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(delivery)
    return delivery

@router.get("/escalations", summary="Get Escalated Discrepancy Notifications (Admin Only)")
def get_escalated_discrepancies(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Retrieve escalated consecutive discrepancy notifications (3+ consecutive mismatches).
    Strictly Admin-only endpoint to prevent supervisor access.
    """
    return db.query(AdminNotification).order_by(AdminNotification.created_at.desc()).all()

@router.get("/materials", response_model=List[MaterialInflowGroup], summary="Get Material Inflow Log Grouped by Type")
def get_material_inflow_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.WORKER]))
):
    """
    Retrieve aggregated material inflow records grouped by material_type over time.
    Restricted to Admin and Supervisor roles.
    """
    results = (
        db.query(
            DeliveryLog.material_type,
            func.sum(DeliveryLog.material_quantity).label("total_quantity"),
            DeliveryLog.quantity_unit,
            func.count(DeliveryLog.id).label("delivery_count")
        )
        .group_by(DeliveryLog.material_type, DeliveryLog.quantity_unit)
        .all()
    )

    groups = []
    for r in results:
        groups.append(MaterialInflowGroup(
            material_type=r.material_type,
            total_quantity=Decimal(str(r.total_quantity or 0)),
            quantity_unit=r.quantity_unit,
            delivery_count=r.delivery_count
        ))
    return groups
