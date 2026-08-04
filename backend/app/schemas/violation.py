import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ViolationFilterQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')
    gate_id: Optional[uuid.UUID] = None
    zone_id: Optional[uuid.UUID] = None
    violation_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ViolationCreateInternal(BaseModel):
    gate_id: Optional[uuid.UUID] = None
    zone_id: Optional[uuid.UUID] = None
    worker_id: Optional[uuid.UUID] = None
    violation_type: str
    helmet_missing: bool = False
    vest_missing: bool = False
    image_url: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class ViolationAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None
    model_config = ConfigDict(extra='forbid')

class ViolationResponse(BaseModel):
    id: uuid.UUID
    gate_id: Optional[uuid.UUID] = None
    zone_id: Optional[uuid.UUID] = None
    worker_id: Optional[uuid.UUID] = None
    violation_type: str
    helmet_missing: bool
    vest_missing: bool
    image_url: Optional[str] = None
    detected_at: datetime
    status: str = "pending"
    acknowledged_by: Optional[uuid.UUID] = None
    acknowledged_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra='forbid')
