import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class EquipmentResponse(BaseModel):
    id: uuid.UUID
    equipment_type: str
    identifier: Optional[str] = None
    location_description: Optional[str] = None
    status: str
    idle_minutes: int
    last_detected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra='forbid')
