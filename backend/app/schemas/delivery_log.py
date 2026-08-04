import uuid
from datetime import datetime
from typing import Optional, Literal
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict

ALLOWED_MATERIAL_TYPES = {"cement", "sand", "bricks", "steel", "pipes", "other"}

class DeliveryLogCreate(BaseModel):
    gate_id: uuid.UUID
    manual_reported_count: int = Field(..., ge=0)
    material_type: str
    material_quantity: Decimal = Field(..., gt=0)
    quantity_unit: str
    vehicle_type: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('material_type')
    @classmethod
    def validate_material_type(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ALLOWED_MATERIAL_TYPES:
            raise ValueError(f"Invalid material_type '{v}'. Allowed values: {sorted(list(ALLOWED_MATERIAL_TYPES))}")
        return v_clean

class DiscrepancyResolveRequest(BaseModel):
    action: Literal["resolve", "flag_for_investigation"] = "resolve"
    notes: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class DeliveryLogResponse(BaseModel):
    id: uuid.UUID
    gate_id: Optional[uuid.UUID] = None
    reported_by: Optional[uuid.UUID] = None
    ai_vehicle_count: Optional[int] = None
    manual_reported_count: int
    material_type: str
    material_quantity: Decimal
    quantity_unit: str
    vehicle_type: Optional[str] = None
    discrepancy_flag: bool
    logged_at: datetime
    discrepancy_resolved: bool = False
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra='forbid')

class MaterialInflowGroup(BaseModel):
    material_type: str
    total_quantity: Decimal
    quantity_unit: str
    delivery_count: int

    model_config = ConfigDict(extra='forbid')
